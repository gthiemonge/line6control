/*
 *  Copyright 2006 (C)  Gregory Thiemonge
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of version 2 of the GNU General Public License as
 *  published by the Free Software Foundation.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Street #330, Boston, MA 02111-1307, USA.
 *
 */

#include <stdint.h>

#include <Python.h>
#include "structmember.h"

#include <alsa/asoundlib.h>
#include <glib.h>

enum {
    DEVICE_POCKETPOD = 1,
    DEVICE_PODXT,
};

const unsigned char pod_version_header[] = { 0x7e, 0x7f, 0x06, 0x02 };

const unsigned char pod_id[] = { 0x00, 0x01, 0x0c };

const unsigned char device_query[] = { 0xf0, 0x7e, 0x7f, 0x06, 0x01, 0xf7 };

static PyModuleDef podc_module;

typedef struct {
    PyObject_HEAD;

    char *name;

    int card;

    int device;
    unsigned int firmware_version;
    int channel_count;

    char init_done;
    char in_dump;
    int dump_patch_id;

    snd_rawmidi_t *input, *output;

    GByteArray *buffer;
} Pod;

static PyObject *PodError;

static int
pod_write_midi (Pod *pod, uint8_t const *buffer, size_t len)
{
    int err;

    printf("[%s:%d] \n", __func__, __LINE__);
    {
        int _i;
        char _ascii[20];
        char const *_d = (char const *)buffer;
        int _l = len;
        for(_i = 0; _i < _l; _i++) {
            if((_i % 16) == 0) {
                if(_i) {
                    _ascii[16] = 0;
                    printf(" %s\n", _ascii);
                }
                printf("0x%06x: ", _i);
            }
            printf("%02hhx ", _d[_i]);
            _ascii[_i % 16] = isgraph(_d[_i]) ? _d[_i] : '.';
        }
        _ascii[_i % 16] = 0;
        for(; _i % 16; _i++) {
            printf("   ");
        }
        printf(" %s\n", _ascii);
    }

    if ((err = snd_rawmidi_write(pod->output, buffer, len)) < 0) {
        PyErr_Format(PodError,
                     "Cannot send data: %s\n",
                     snd_strerror(err));
        return err;
    }

    return err;
}

static int
pod_send_sysex (Pod *pod, uint8_t const *buffer, size_t len)
{
    printf("[%s:%d] \n", __func__, __LINE__);

    return pod_write_midi(pod, buffer, len);
}

static int
pod_parse_cc (Pod *self)
{
    PyObject *ret;
    char param, value;

    param = self->buffer->data[1];
    value = self->buffer->data[2];

    self->buffer = g_byte_array_remove_range(self->buffer, 0, 3);

    ret = PyObject_CallMethod((PyObject *)self, "param_handler",
            "bb", param, value);
    if(ret == NULL) {
        PyErr_Print();
        return 0;
    }

    Py_DECREF(ret);
    return 1;
}

static int
pod_parse_pc (Pod *self)
{
    PyObject *ret;
    char value;

    value = self->buffer->data[1];

    self->buffer = g_byte_array_remove_range(self->buffer, 0, 2);

    ret = PyObject_CallMethod((PyObject *)self, "program_handler",
            "b", value);
    if(ret == NULL) {
        PyErr_Print();
        return 0;
    }

    Py_DECREF(ret);
    return 1;
}

static int
pod_podxt_get_current_patch (Pod *pod)
{
    uint8_t sysex_buffer[] = {
        0xf0, 0x00, 0x01, 0x0c,
        0x03, 0x75, 0xf7
    };

    return pod_send_sysex(pod, sysex_buffer, sizeof(sysex_buffer));
}

static int
pod_pocketpod_get_current_patch (Pod *pod)
{
    uint8_t sysex_buffer[] = {
        0xf0, 0x00, 0x01, 0x0c,
        0x01, 0x00, 0x01, 0xf7
    };

    return pod_send_sysex(pod, sysex_buffer, sizeof(sysex_buffer));
}

static int
pod_get_current_patch (Pod *pod)
{
    switch (pod->device) {
    case DEVICE_POCKETPOD:
        return pod_pocketpod_get_current_patch(pod);
        break;
    case DEVICE_PODXT:
        return pod_podxt_get_current_patch(pod);
        break;
    }
    return 0;
}

static int
pod_podxt_request_patch (Pod *pod, int patch_id)
{
    uint8_t sysex_buffer[] = {
        0xf0, 0x00, 0x01, 0x0c,
        0x03, 0x73, patch_id > 0x3f, patch_id,
        0x00, 0x00, 0xf7
    };

    return pod_send_sysex(pod, sysex_buffer, sizeof(sysex_buffer));
}

static int
pod_pocketpod_request_patch (Pod *pod, int patch_id)
{
    uint8_t sysex_buffer[] = {
        0xf0, 0x00, 0x01, 0x0c,
        0x01, 0x00, 0x00, patch_id, 0xf7
    };

    return pod_send_sysex(pod, sysex_buffer, sizeof(sysex_buffer));
}

static int
pod_request_patch (Pod *pod, int patch_id)
{
    switch (pod->device) {
    case DEVICE_POCKETPOD:
        return pod_pocketpod_request_patch(pod, patch_id);
        break;
    case DEVICE_PODXT:
        return pod_podxt_request_patch(pod, patch_id);
        break;
    }
    return 0;
}

static gboolean
pod_list_patches (gpointer data)
{
    Pod *pod = (Pod *)data;

    pod->in_dump = 1;

    pod_request_patch(pod, pod->dump_patch_id);

    return FALSE;
}

static int
pod_parse_sysex (Pod *pod)
{
    PyObject *ret;
    unsigned int sysex_len;
    unsigned char *eos;

    if ((pod->buffer->data[0] & 0xf0) != 0xf0) {
        return 0;
    }

    eos = memchr(pod->buffer->data,
                 0xf7, pod->buffer->len);
    if (!eos) {
        return 0;
    }

    sysex_len = (eos - pod->buffer->data) + 1;
    printf("[%s:%d] sysex_len = %u\n", __func__, __LINE__,
           sysex_len);
    {
        int _i;
        char _ascii[20];
        char const *_d = (char const *)pod->buffer->data;
        int _l = sysex_len;
        for(_i = 0; _i < _l; _i++) {
            if((_i % 16) == 0) {
                if(_i) {
                    _ascii[16] = 0;
                    printf(" %s\n", _ascii);
                }
                printf("0x%06x: ", _i);
            }
            printf("%02hhx ", _d[_i]);
            _ascii[_i % 16] = isgraph(_d[_i]) ? _d[_i] : '.';
        }
        if(_i % 16) {
            _ascii[_i % 16] = 0;
            for(; _i % 16; _i++) {
                printf("   ");
            }
            printf(" %s\n", _ascii);
        }
    }

    if (sysex_len == 17 &&
        memcmp(pod->buffer->data + 1,
               pod_version_header,
               sizeof(pod_version_header)) == 0) {

        uint32_t device_id = 0;
        uint32_t firmware_version = 0;
        char tmp[5];

        if (memcmp(pod->buffer->data + 5,
                   pod_id, sizeof(pod_id)) != 0) {
            printf("Warning cannot get POD id from sysex\n");
        }

        device_id = pod->buffer->data[8] << 16 |
            pod->buffer->data[9] << 8 |
            pod->buffer->data[10];

        switch (device_id) {
        case 0:
            pod->device = DEVICE_POCKETPOD;
            break;
        case 0x30002:
            pod->device = DEVICE_PODXT;
            break;
        }

        switch (pod->device) {
        case DEVICE_POCKETPOD:
            pod->channel_count = 123;
            memcpy(tmp, pod->buffer->data + 12, 4);
            tmp[4] = '\0';
            firmware_version = strtol(tmp, NULL, 10);
            break;
        case DEVICE_PODXT:
            pod->channel_count = 127;
            firmware_version = pod->buffer->data[12] * 1000 +
                pod->buffer->data[13] * 100 +
                pod->buffer->data[14] * 10 +
                pod->buffer->data[15];
            break;
        }

        printf("[%s:%d] device_id=%x, device=%x, firmware_version=%u\n",
               __func__, __LINE__, device_id, pod->device, firmware_version);

        pod->firmware_version = firmware_version;

        pod->buffer =
            g_byte_array_remove_range(pod->buffer, 0, sysex_len);

        pod->dump_patch_id = 0;
        g_idle_add(pod_list_patches, pod);

        return 1;
    } else if((sysex_len == 168 && pod->buffer->data[5] == 0x74) ||
              (sysex_len == 152 &&
               pod->buffer->data[5] == 0x01 &&
               pod->buffer->data[6] == 0x00) ||
              (sysex_len == 151 &&
               pod->buffer->data[5] == 0x01 &&
               pod->buffer->data[6] == 0x01)) { /* Dump */
        char preset_name[64] = { '\0' };
        PyObject *preset_dict;
        unsigned int i;
        unsigned int j;

        preset_dict = PyDict_New();

        switch(pod->device) {
        case DEVICE_POCKETPOD:
            i = 0;
            for (j = sysex_len - 33; j < sysex_len - 1; j += 2) {
                preset_name[i++] =
                    pod->buffer->data[j] << 4 |
                    pod->buffer->data[j + 1];
            }
            preset_name[i] = '\0';

            i = 4;
            for(j = sysex_len - 142 - 1; j < sysex_len - 33; j += 2) {

                PyObject *k = PyLong_FromLong(i++);
                PyObject *v = PyLong_FromLong(
                    pod->buffer->data[j] << 4 |
                    pod->buffer->data[j + 1]);

                PyDict_SetItem(preset_dict, k, v);
            }
            break;
        case DEVICE_PODXT:
            memcpy(preset_name,
                   pod->buffer->data + 7,
                   16);
            preset_name[16] = '\0';

            for(i = 0; i < sysex_len - 1 - 0x27; i++) {
                PyObject *k = PyLong_FromLong(i);
                PyObject *v = PyLong_FromLong(pod->buffer->data[0x27 + i]);

                PyDict_SetItem(preset_dict, k, v);
            }

            break;
        }

        if (pod->in_dump) {
            ret = PyObject_CallMethod((PyObject *)pod, "on_patch_update",
                                      "isO", pod->dump_patch_id,
                                      preset_name, preset_dict);
        } else {
            ret = PyObject_CallMethod((PyObject *)pod, "on_current_patch", "");
        }

        pod->buffer =
            g_byte_array_remove_range(pod->buffer, 0, sysex_len);

        if(ret == NULL) {
            PyErr_Print();
            return 0;
        }

        if (pod->init_done == 0) {
            if (pod->in_dump) {
                if (pod->dump_patch_id < pod->channel_count) {
                    pod->dump_patch_id++;
                    g_idle_add(pod_list_patches, pod);
                } else {
                    pod->in_dump = 0;
                    pod->dump_patch_id = 0;

                    pod_get_current_patch(pod);
                }
            } else {
                ret = PyObject_CallMethod((PyObject *)pod, "run", "");
                if(ret == NULL) {
                    PyErr_Print();
                    return 0;
                }
                pod->init_done = 1;
            }
        }

        return 1;
    } else if(pod->buffer->len >= 12 &&
            pod->buffer->data[5] == 0x56) {
        switch(pod->buffer->data[6]) {
            case 0x04: {
                           pod->buffer =
                               g_byte_array_remove_range(pod->buffer, 0, 12);

                           return 1;
                       }
                       break;
            case 0x17: {
                           pod->buffer =
                               g_byte_array_remove_range(pod->buffer, 0, 12);

                           return 1;
                       }
                       break;
        }
    } else if(pod->buffer->len >= 7 &&
            pod->buffer->data[5] == 0x72) { /* Finished dump */
        pod->buffer = g_byte_array_remove_range(pod->buffer, 0, 7);
        return 1;
    } else if(pod->buffer->len >= 9 &&
            pod->buffer->data[5] == 0x24) { /* Save */
        pod->buffer =
            g_byte_array_remove_range(pod->buffer, 0, 9);
        return 1;
    } else if(pod->buffer->data[5] == 0x0f) { /* Clip */
        pod->buffer =
            g_byte_array_remove_range(pod->buffer, 0, 7);
        return 1;
    } else {
        printf("Unknown sysex\n");
        pod->buffer =
            g_byte_array_remove_range(pod->buffer, 0, pod->buffer->len);
    }

    return 0;
}

static int
pod_parse_buffer (Pod *self)
{
    int ret = -1;

    if(self->buffer == NULL ||
       self->buffer->len == 0)
        return 0;

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    switch(self->buffer->data[0]) {
        case 0xB0:
        case 0xB2:
            ret = pod_parse_cc(self);
            break;
        case 0xC0:
        case 0xC2:
            ret = pod_parse_pc(self);
            break;
        case 0xF0:
        case 0xF2:
        case 0xF5:
            ret = pod_parse_sysex(self);
            break;
        default:
            abort();
            break;
    }

    PyGILState_Release(gstate);

    return ret;
}

static gboolean
pod_idle (gpointer data)
{
    Pod *self = (Pod *)data;
    int npfds;
    struct pollfd *pfds;
    unsigned char buf[4096];
    int err, len;
    unsigned short revents = 0;
    int done = 0;

    while(pod_parse_buffer(self) != 0);

    npfds = snd_rawmidi_poll_descriptors_count(self->input);
    pfds = calloc(npfds, sizeof(struct pollfd));
    snd_rawmidi_poll_descriptors(self->input, pfds, npfds);

    do {
        err = poll(pfds, npfds, 50);
        if(err < 0) { // error
            PyErr_SetString(PodError,
                    "Error while polling file descriptors");
            free(pfds);
            return TRUE;
        }
        if(err == 0) {// timeout
            free(pfds);
            return TRUE;
        }

        if(self->input == NULL) {
            free(pfds);
            return TRUE;
        }

        if ((err =
                    snd_rawmidi_poll_descriptors_revents(self->input,
                        pfds, npfds,
                        &revents)) < 0) {
            PyErr_Format(PodError, "Cannot get poll events: %s\n",
                    snd_strerror(errno));
            free(pfds);
            return TRUE;
        }
        if (revents & (POLLERR | POLLHUP)) {
            free(pfds);
            return TRUE;
        }
        if (!(revents & POLLIN)) {
            free(pfds);
            return TRUE;
        }
        err = snd_rawmidi_read(self->input, buf, sizeof(buf));
        if (err < 0) {
            PyErr_Format(PodError, "Cannot read from port: %s\n",
                    snd_strerror(err));
            free(pfds);
            return TRUE;
        }
        len = err;

        self->buffer =
            g_byte_array_append(self->buffer, buf, len);

        done = pod_parse_buffer(self);
    } while (done == 0);

    free(pfds);
    return TRUE;
}

static PyObject *
pypod_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Pod *self;

    if(!(self = (Pod *)type->tp_alloc(type, 0)))
        return NULL;

    return (PyObject *)self;
}

static int
pypod_init(Pod *self, PyObject *args, PyObject *kwds)
{
    int card;
    char name[32];
    int err;

    if(!PyArg_ParseTuple(args, "i", &card))
        return -1;

    self->card = card;
    self->buffer = g_byte_array_new();

    self->name = strdup("PODxt");

    snprintf(name, 32, "hw:%d", self->card);

    if ((err = snd_rawmidi_open(&(self->input),
                    &(self->output), name, 0)) < 0) {
        PyErr_Format(PodError, "Cannot open device '%s': %s\n",
                name, snd_strerror(err));
        return -1;
    }

    snd_rawmidi_read(self->input, NULL, 0);
    snd_rawmidi_nonblock(self->input, 1);

    pod_send_sysex(self, device_query, sizeof(device_query));

    g_idle_add(pod_idle, self);

    return 0;
}

static PyObject *
pypod_close (Pod *self, PyObject *args)
{
    if(!PyArg_ParseTuple(args, ""))
        return NULL;

    if(self->input != NULL) {
        snd_rawmidi_close(self->input);
        self->input = NULL;
    }

    if(self->output != NULL) {
        snd_rawmidi_close(self->output);
        self->output = NULL;
    }

    //self->ob_type->tp_free((PyObject*)self);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_send_cc (Pod *self, PyObject *args)
{
    unsigned char buf[3];
    char param, value;

    if(!PyArg_ParseTuple(args, "bb", &param, &value))
        return NULL;

    buf[0] = 0xB0;
    buf[1] = param;
    buf[2] = value;

    pod_write_midi(self, buf, 3);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_send_pc (Pod *self, PyObject *args)
{
    unsigned char buf[2];
    char value;

    if(!PyArg_ParseTuple(args, "b", &value))
        return NULL;

    buf[0] = 0xC0;
    buf[1] = value;

    pod_write_midi(self, buf, 2);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_param_handler (Pod *self, PyObject *args)
{
    char param, value;

    if(!PyArg_ParseTuple(args, "bb", &param, &value))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_program_handler (Pod *self, PyObject *args)
{
    char value;

    if(!PyArg_ParseTuple(args, "b", &value))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_run (Pod *self, PyObject *args)
{
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_on_patch_update (Pod *self, PyObject *args)
{
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_get_current_patch (Pod *self, PyObject *args)
{
    pod_get_current_patch(self);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_on_current_patch (Pod *self, PyObject *args)
{
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef pod_methods[] = {
    {"run", (PyCFunction)pypod_run, METH_VARARGS},
    {"close", (PyCFunction)pypod_close, METH_VARARGS},

    {"send_cc", (PyCFunction)pypod_send_cc, METH_VARARGS},
    {"send_pc", (PyCFunction)pypod_send_pc, METH_VARARGS},

    {"param_handler", (PyCFunction)pypod_param_handler, METH_VARARGS},
    {"program_handler", (PyCFunction)pypod_program_handler, METH_VARARGS},
    {"get_current_patch", (PyCFunction)pypod_get_current_patch, METH_VARARGS},
    {"on_patch_update", (PyCFunction)pypod_on_patch_update, METH_VARARGS},
    {"on_current_patch", (PyCFunction)pypod_on_current_patch, METH_VARARGS},
    {NULL}
};

static PyMemberDef pod_members[] = {
    {"device", T_INT, offsetof(Pod, device), 0,
        "device identifier"},
    {"firmware_version", T_INT, offsetof(Pod, firmware_version), 0,
        "firmware_version"},
    {"channel_count", T_INT, offsetof(Pod, channel_count), 0,
        "number of channels"},
    {NULL}
};

static void
pypod_dealloc(Pod* self)
{
}

static PyModuleDef podc_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "podc",
    .m_doc = "",
    .m_size = -1,
};

static PyTypeObject PodType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "podc.Pod",
    .tp_doc = "Pod object",
    .tp_basicsize = sizeof(Pod),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_new = pypod_new,
    .tp_init = (initproc)pypod_init,
    .tp_dealloc = (destructor)pypod_dealloc,
    .tp_methods = pod_methods,
    .tp_members = pod_members,
};

PyMODINIT_FUNC
PyInit_podc(void)
{
    PyObject* m;

    if (PyType_Ready(&PodType) < 0) {
        return NULL;
    }

    m = PyModule_Create(&podc_module);
    if (m == NULL) {
        return NULL;
    }

    PodError = PyErr_NewException("pod.PodError", NULL, NULL);

    Py_INCREF(&PodType);
    if (PyModule_AddObject(m, "Pod", (PyObject *)&PodType)) {
        Py_DECREF(&PodType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(PodError);
    PyModule_AddObject(m, "PodError", PodError);

    PyModule_AddIntMacro(m, DEVICE_POCKETPOD);
    PyModule_AddIntMacro(m, DEVICE_PODXT);

    return m;
}
