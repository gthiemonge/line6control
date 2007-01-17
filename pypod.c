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

#include <Python.h>
#include <alsa/asoundlib.h>
#include <glib.h>

// from line6usb driver
const char pod_version_header [] = { 0xf2, 0x7e, 0x7f, 0x06, 0x02 };

static PyTypeObject PodType;

typedef struct {
    PyObject_HEAD;

    char *name;

    int card;

    snd_rawmidi_t *input, *output;

    GByteArray *buffer;
} Pod;

static PyObject *PodError;

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
pod_parse_sysex (Pod *pod)
{
    PyObject *ret;

    if(pod->buffer->len < 5)
        return 0;

    if(pod->buffer->len >= 17 &&
            memcmp(pod->buffer->data,
                pod_version_header, sizeof(pod_version_header)) == 0) {
        PyObject *buf;
        int i;

        buf = PyList_New(17);
        for(i = 0; i < 17; i++) {
            PyObject *o = Py_BuildValue("b", pod->buffer->data[i]);
            PyList_SET_ITEM(buf, i, o);
        }
        ret = PyObject_CallMethod((PyObject *)pod, "sysex_handler",
                "O", buf);

        pod->buffer = 
            g_byte_array_remove_range(pod->buffer, 0, 17);

        if(ret == NULL) {
            PyErr_Print();
            return 0;
        }

        return 1;
    } else if(pod->buffer->len >= 168 &&
            pod->buffer->data[5] == 0x74) { /* Dump */
        PyObject *buf;
        int i;

        buf = PyList_New(168);
        for(i = 0; i < 168; i++) {
            PyObject *o = Py_BuildValue("b", pod->buffer->data[i]);
            PyList_SET_ITEM(buf, i, o);
        }
        ret = PyObject_CallMethod((PyObject *)pod, "sysex_handler",
                "O", buf);

        pod->buffer = 
            g_byte_array_remove_range(pod->buffer, 0, 168);

        if(ret == NULL) {
            PyErr_Print();
            return 0;
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
        PyObject *buf;
        int i;

        buf = PyList_New(7);
        for(i = 0; i < 7; i++) {
            PyObject *o = Py_BuildValue("b", pod->buffer->data[i]);
            PyList_SET_ITEM(buf, i, o);
        }
        ret = PyObject_CallMethod((PyObject *)pod, "sysex_handler",
                "O", buf);			
        pod->buffer = g_byte_array_remove_range(pod->buffer, 0, 7);

        if(ret == NULL) {
            PyErr_Print();
            return 0;
        }

        return 1;
    } else if(pod->buffer->len >= 9 &&
            pod->buffer->data[5] == 0x24) { /* Save */
        pod->buffer = 
            g_byte_array_remove_range(pod->buffer, 0, 9);
        return 1;
    } else {
        /*
           int i;
           printf("Unknown sysex\n");
           for(i = 0; i < pod->buffer->len; i++) {
           if((i % 8) == 0)
           printf("\n");
           printf("%02hhx ", pod->buffer->data[i]);
           }b
           printf("\n");	*/
    }

    return 0;
}

static int
pod_parse_buffer (Pod *self)
{
    int i;

    if(self->buffer->len == 0)
        return 0;

    switch(self->buffer->data[0]) {
        case 0xB0:
            if(self->buffer->len >= 3) {
                self->buffer =
                    g_byte_array_remove_range(self->buffer, 0, 3);
                return 1;
            }

            break;
        case 0xB2:
            return pod_parse_cc(self);
            break;
        case 0xC0:
            if(self->buffer->len >= 2) {
                self->buffer =
                    g_byte_array_remove_range(self->buffer, 0, 2);
                return 1;
            }
            break;
        case 0xC2:
            return pod_parse_pc(self);
            break;
        case 0xF2:
        case 0xF5:
            return pod_parse_sysex(self);
            break;
    }

    printf("%d bytes not processed !!\n", self->buffer->len);

    for(i = 0; i < self->buffer->len; i++) {
        if((i % 8) == 0)
            printf("\n");
        printf("%02hhx ", self->buffer->data[i]);
    }
    printf("\n");


    return 0;
}

static gboolean
pod_idle (gpointer data)
{
    Pod *self = (Pod *)data;
    int npfds;
    struct pollfd *pfds;
    unsigned char buf[256];
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
    int card;
    char name[32];
    int err;

    if(!PyArg_ParseTuple(args, "i", &card))
        return NULL;

    if(!(self = (Pod *)type->tp_alloc(type, 0)))
        return NULL;

    self->card = card;
    self->buffer = g_byte_array_new();

    self->name = strdup("PODxt");

    snprintf(name, 32, "hw:%d", self->card);

    if ((err = snd_rawmidi_open(&(self->input),
                    &(self->output), name, 0)) < 0) {
        PyErr_Format(PodError, "Cannot open device '%s': %s\n",
                name, snd_strerror(err));
        return NULL;
    }

    snd_rawmidi_read(self->input, NULL, 0);
    snd_rawmidi_nonblock(self->input, 1);

    g_idle_add(pod_idle, self);

    return (PyObject *)self;
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

    //	self->ob_type->tp_free((PyObject*)self);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_send_cc (Pod *self, PyObject *args)
{
    signed char buf[3];
    int err;
    char param, value;

    if(!PyArg_ParseTuple(args, "bb", &param, &value))
        return NULL;

    buf[0] = 0xB0;
    buf[1] = param;
    buf[2] = value;

    if ((err = snd_rawmidi_write(self->output, buf, 3)) < 0) {
        PyErr_Format(PodError,
                "Cannot send data: %s\n",
                snd_strerror(err));
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_send_pc (Pod *self, PyObject *args)
{
    signed char buf[2];
    int err;
    char value;

    if(!PyArg_ParseTuple(args, "b", &value))
        return NULL;

    buf[0] = 0xC0;
    buf[1] = value;

    if ((err = snd_rawmidi_write(self->output, buf, 2)) < 0) {
        PyErr_Format(PodError,
                "Cannot send data: %s\n",
                snd_strerror(err));
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pypod_send_sysex (Pod *self, PyObject *args)
{
    PyObject *buffer, *integer;
    char *tmp;
    int len, err, i;

    if(!PyArg_UnpackTuple(args, "send_sysex", 1, 200, &buffer))
        return NULL;

    len = PySequence_Size(buffer);
    tmp = malloc(sizeof(char) * len);

    for(i = 0; i < len; i++) {
        integer = PySequence_GetItem(buffer, i);
        tmp[i] = (char)PyInt_AS_LONG(integer);
    }

    if ((err = snd_rawmidi_write(self->output, tmp, len)) < 0) {
        PyErr_Format(PodError,
                "Cannot send data: %s\n",
                snd_strerror(err));
        free(tmp);
        return NULL;
    }
    free(tmp);


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
pypod_sysex_handler (Pod *self, PyObject *args)
{
    PyObject *buffer;

    if(!PyArg_ParseTuple(args, "O", &buffer))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef pod_methods[] = {
    {"close", (PyCFunction)pypod_close, METH_VARARGS},

    {"send_cc", (PyCFunction)pypod_send_cc, METH_VARARGS},
    {"send_pc", (PyCFunction)pypod_send_pc, METH_VARARGS},
    {"send_sysex", (PyCFunction)pypod_send_sysex, METH_VARARGS},

    {"param_handler", (PyCFunction)pypod_param_handler, METH_VARARGS},
    {"program_handler", (PyCFunction)pypod_program_handler, METH_VARARGS},
    {"sysex_handler", (PyCFunction)pypod_sysex_handler, METH_VARARGS},
    {NULL, NULL}
};

static void
pypod_dealloc(Pod* self)
{
}

static PyTypeObject PodType = {
        PyObject_HEAD_INIT(NULL)
            0,
        "podc.Pod",
        sizeof(Pod),
        0,                         /*tp_itemsize*/
        (destructor)pypod_dealloc,                         /*tp_dealloc*/
        0,                         /*tp_print*/
        0,/*tp_getattr*/
        0,                         /*tp_setattr*/
        0,                         /*tp_compare*/
        0,                         /*tp_repr*/
        0,                         /*tp_as_number*/
        0,                         /*tp_as_sequence*/
        0,                         /*tp_as_mapping*/
        0,                         /*tp_hash */
        0,                         /*tp_call*/
        0,                         /*tp_str*/
        0,                         /*tp_getattro*/
        0,                         /*tp_setattro*/
        0,                         /*tp_as_buffer*/
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE |
            Py_TPFLAGS_HAVE_GC,        /*tp_flags*/
        "Pod device",              /*tp_doc*/
        (traverseproc)0,	/* tp_traverse */
        (inquiry)0,		/* tp_clear */
        (richcmpfunc)0,			/* tp_richcompare */
        0,	/* tp_weaklistoffset */
        (getiterfunc)0,			/* tp_iter */
        (iternextfunc)0,			/* tp_iternext */
        pod_methods,			/* tp_methods */
        0,					/* tp_members */
        0,			/* tp_getset */
        (PyTypeObject *)0,			/* tp_base */
        (PyObject *)0,			/* tp_dict */
        0,					/* tp_descr_get */
        0,					/* tp_descr_set */
        0,	/* tp_dictoffset */
        (initproc)0,		/* tp_init */
        (allocfunc)0,			/* tp_alloc */
        (newfunc)pypod_new,				/* tp_new */
        (freefunc)0,		/* tp_free */
        (inquiry)0,				/* tp_is_gc */
        (PyObject *)0,			/* tp_bases */
    };

void
initpodc (void)
{
    PyObject* m, *d;

    PodType.tp_new = pypod_new;
    if (PyType_Ready(&PodType) < 0)
        return;

    m = Py_InitModule("podc", NULL);
    d = PyModule_GetDict(m);

    PodError = PyErr_NewException("pod.PodError", NULL, NULL);

    Py_INCREF(&PodType);
    PyModule_AddObject(m, "Pod", (PyObject *)&PodType);
    //	PyDict_SetItemString(d, "Pod", (PyObject *)&PodType);

    Py_INCREF(PodError);
    PyModule_AddObject(m, "PodError", PodError);
}
