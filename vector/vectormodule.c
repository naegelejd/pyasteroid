
/* Use this file as a template to start implementing a module that
   also declares object types. All occurrences of 'Vector2D' should be changed
   to something reasonable for your objects. After that, all other
   occurrences of 'vector' should be changed to something reasonable for your
   module. If your module is named foo your sourcefile should be named
   foomodule.c.

   You will probably want to delete all references to 'x_attr' and add
   your own types of attributes instead.  Maybe you want to name your
   local variables other than 'self'.  If your object type is needed in
   other files, you'll have to create a file "foobarobject.h"; see
   intobject.h for an example. */

/* Vector2D objects */

#include "Python.h"
#include "structmember.h"
#include "math.h"

static PyObject *ErrorObject;

typedef struct {
    PyObject_HEAD
	double		x;
	double		y;
} Vector2D;

static PyTypeObject Vector2D_Type;
#define SEQ_LENGTH	2
#define Vector2D_Check(v)      (Py_TYPE(v) == &Vector2D_Type)

static double
dot(double x1, double y1, double x2, double y2)
{
	return (x1 * x2) + (y1 * y2);
}

static double
length(double x, double y)
{
	return sqrt((x * x) + (y * y));
}

/* Helpers from Pete Shinner's Pygame library */
static int
FloatFromObj (PyObject* obj, float* val)
{
    float f= (float)PyFloat_AsDouble (obj);

    if (f==-1 && PyErr_Occurred()) {
		PyErr_Clear ();
        return 0;
	}

    *val = f;
    return 1;
}

static int
FloatFromObjIndex (PyObject* obj, int _index, float* val)
{
    int result = 0;
    PyObject* item;
    item = PySequence_GetItem (obj, _index);
    if (item)
    {
        result = FloatFromObj (item, val);
        Py_DECREF (item);
    }
    return result;
}

static int
TwoFloatsFromObj (PyObject* obj, float* val1, float* val2)
{
    if (PyTuple_Check (obj) && PyTuple_Size (obj) == 1)
        return TwoFloatsFromObj (PyTuple_GET_ITEM (obj, 0), val1, val2);

    if (!PySequence_Check (obj) || PySequence_Length (obj) != 2)
        return 0;

    if (!FloatFromObjIndex (obj, 0, val1) || !FloatFromObjIndex (obj, 1, val2))
        return 0;

    return 1;
}
/* End of Pygame helpers */

static int
TwoFloatsFromVector2D(PyObject *obj, double *x, double *y) {
	if (PyObject_TypeCheck(obj, &Vector2D_Type)) {
		*x = ((Vector2D *)obj)->x;
		*y = ((Vector2D *)obj)->y;
		return 1;
	}
	if (! TwoFloatsFromObj(obj, (float *)x, (float *)y))
		return 0;
	else
		return 1;
}

/* Vector2D methods */

static void
Vector2D_dealloc(Vector2D *self)
{
    PyObject_Del(self); // self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Vector2D_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	Vector2D *self;

	self = (Vector2D *)type->tp_alloc(type, 0);
	if (self != NULL) {
		self->x = 0.0;
		self->y = 0.0;
	}
	return (PyObject *)self;
}

static int
Vector2D_init(Vector2D *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = {"X", "Y", NULL};
	if (! PyArg_ParseTupleAndKeywords(args, kwds, "dd", kwlist,
				&self->x, &self->y))
		return -1;

	return 0;
}

static Vector2D *
Vector2D_zero(Vector2D *self)
{
	return (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
}

static Vector2D *
Vector2D_one(Vector2D *self)
{
	Vector2D *one = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	one->x = 1.0;
	one->y = 1.0;
	return one;
}

static Vector2D *
Vector2D_copy(Vector2D *self)
{
	Vector2D *copy = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	copy->x = self->x;
	copy->y = self->y;
	return copy;
}

static Vector2D *
Vector2D_normal(Vector2D *self)
{
	double l;
	Vector2D *norm = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	norm->x = self->x;
	norm->y = self->y;
	l = length(self->x, self->y);
	if (length > 0) {
		norm->x /= l;
		norm->y /= l;
	}
	return norm;
}

static PyObject *
Vector2D_dot(Vector2D *self, PyObject *args)
{
	double d;
	double x;
	double y;
	Vector2D *other;
    if (!PyArg_ParseTuple(args, "O:dot", &other))
		return NULL;
	if (! TwoFloatsFromVector2D((PyObject *)other, &x, &y)) {
		PyErr_SetString(PyExc_TypeError, "Argument must be a Vector2D");
		return NULL;
	}
	d = dot(self->x, self->y, x, y);
	return PyFloat_FromDouble(d);
}

static PyObject *
Vector2D_angle(Vector2D *self, PyObject *args)
{
	double d, l1, l2, x, y, ang;
	Vector2D *other;
    if (!PyArg_ParseTuple(args, "O:angle", &other))
		return NULL;
	if (! TwoFloatsFromVector2D((PyObject *)other, &x, &y)) {
		PyErr_SetString(PyExc_TypeError, "Argument must be a Vector2D");
		return NULL;
	}
	d = dot(self->x, self->y, x, y);
	l1 = length(self->x, self->y);
	l2 = length(x, y);
	ang = acos(d / (l1 * l2));
	return PyFloat_FromDouble(ang);
}

static PyObject *
Vector2D_rotate(Vector2D *self, PyObject *args)
{
	double th;
	if (!PyArg_ParseTuple(args, "d:rotate", &th))
		return NULL;
	Vector2D *result = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	result->x = (self->x * cos(th)) - (self->y * sin(th));
	result->y = (self->x * sin(th)) + (self->y * cos(th));
	return (PyObject *)result;
}

static PyObject *
Vector2D_length(Vector2D *self)
{
	double len;
	len = length(self->x, self->y);
	return PyFloat_FromDouble(len);
}

static PyObject *
Vector2D_distance(Vector2D *self, PyObject *args)
{
	double d, x, y;
	Vector2D *other;
    if (!PyArg_ParseTuple(args, "O:distance", &other))
		return NULL;
	if (! TwoFloatsFromVector2D((PyObject *)other, &x, &y)) {
		PyErr_SetString(PyExc_TypeError, "Argument must be a Vector2D");
		return NULL;
	}
	d = length((x - self->x), (y - self->y));
	return PyFloat_FromDouble(d);
}

static Vector2D *
Vector2D_lerp(Vector2D *self, PyObject *args)
{
	double time, x, y;
	Vector2D *other;
    if (!PyArg_ParseTuple(args, "Od:lerp", &other, &time))
		return NULL;
	if (! TwoFloatsFromVector2D((PyObject *)other, &x, &y)) {
		PyErr_SetString(PyExc_TypeError, "Argument must be a Vector2D");
		return NULL;
	}
	if (time < 0)
		time = 0.0;
	else if (time > 1)
		time = 1.0;

	other->x = self->x + time * (other->x - self->x);
	other->y = self->y + time * (other->y - self->y);
	return other;
}

static PyMethodDef Vector2D_methods[] = {
	{"zeros", (PyCFunction)Vector2D_zero, METH_NOARGS|METH_STATIC,
			PyDoc_STR("zeros() -> Vector2D(0, 0)")},
	{"ones", (PyCFunction)Vector2D_one, METH_NOARGS|METH_STATIC,
			PyDoc_STR("ones() -> Vector2D(1, 1)")},
	{"copy", (PyCFunction)Vector2D_copy, METH_NOARGS,
			PyDoc_STR("copy() -> return a copy of this Vector2D")},
	{"normal", (PyCFunction)Vector2D_normal, METH_NOARGS,
			PyDoc_STR("normal() -> return a normalized copy of this Vector2D")},
	{"dot", (PyCFunction)Vector2D_dot, METH_VARARGS,
			PyDoc_STR("dot(other) -> return the dot product of this and other")},
	{"angle", (PyCFunction)Vector2D_angle, METH_VARARGS,
			PyDoc_STR("angle(other) -> returns the angle between this and other")},
	{"rotate", (PyCFunction)Vector2D_rotate, METH_VARARGS,
			PyDoc_STR("rotate(theta) -> return rotated copy of this")},
	{"length", (PyCFunction)Vector2D_length, METH_NOARGS,
			PyDoc_STR("length() -> None")},
	{"distance", (PyCFunction)Vector2D_distance, METH_VARARGS,
			PyDoc_STR("distance(v2) -> float")},
	{"lerp", (PyCFunction)Vector2D_lerp, METH_VARARGS,
			PyDoc_STR("lerp(other, time) -> lerp between this and other. Time clamped between 0 and 1")},
    {NULL,              NULL}           /* sentinel */
};

/* Using getseters instead of members */
/*
static PyMemberDef Vector2D_members[] = {
	{"X", T_FLOAT, offsetof(Vector2D, x), 0, "X coordinate"},
	{"Y", T_FLOAT, offsetof(Vector2D, y), 0, "Y coordinate"},
};
*/

static PyObject *
Vector2D_getX(Vector2D *self, void *closure)
{
	//Py_INCREF(self->x);
	return PyFloat_FromDouble(self->x);
}

static int
Vector2D_setX(Vector2D *self, PyObject *value, void *closure)
{
	if (value == NULL) {
		PyErr_SetString(PyExc_TypeError, "Cannot delete the X coordinate");
		return -1;
	}
	if (! PyNumber_Check(value)) {
		PyErr_SetString(PyExc_TypeError, "X coordinate must be a number");
		return -1;
	}

	//Py_DECREF(self->x);
	//Py_INCREF(value);
	self->x = PyFloat_AsDouble(value);

	return 0;
}

static PyObject *
Vector2D_getY(Vector2D *self, void *closure)
{
	//Py_INCREF(self->y);
	return PyFloat_FromDouble(self->y);
}

static int
Vector2D_setY(Vector2D *self, PyObject *value, void *closure)
{
	if (value == NULL) {
		PyErr_SetString(PyExc_TypeError, "Cannot delete the Y coordinate");
		return -1;
	}
	if (! PyNumber_Check(value)) {
		PyErr_SetString(PyExc_TypeError, "Y coordinate must be a number");
		return -1;
	}

	//Py_DECREF(self->y);
	//Py_INCREF(value);
	self->y = PyFloat_AsDouble(value);

	return 0;
}

static PyGetSetDef Vector2D_getsetters[] = {
	{"X", (getter)Vector2D_getX, (setter)Vector2D_setX, "X coordinate", NULL},
	{"Y", (getter)Vector2D_getY, (setter)Vector2D_setY, "Y coordinate", NULL},
	{NULL}		/* Sentinel */
};

static PyObject *
Vector2D_repr(Vector2D *obj)
{
	char dstr[32];
	sprintf(dstr, "%.3f, %.3f", obj->x, obj->y);
	return PyString_FromFormat("<%s(%s)>",
			Py_TYPE(obj)->tp_name, dstr);
}

static int
Vector2D_compare(Vector2D *obj1, Vector2D *obj2)
{
	if((obj1->x == obj2->x) && (obj1->y == obj2->y))
		return 0;
	else if(length(obj1->x, obj1->y) < length(obj2->x, obj2->y))
		return -1;
	else
		return 1;
}

static PyObject *
Vector2D_add(Vector2D *self, PyObject *a)
{
	double x;
	double y;
	if (! TwoFloatsFromVector2D(a, &x, &y)) {
		PyErr_SetString(PyExc_TypeError, "Addend must be vector-like");
		return NULL;
	}
	Vector2D *result = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	result->x = self->x + x;
	result->y = self->y + y;
	return (PyObject *)result;
}

static PyObject *
Vector2D_sub(Vector2D *self, PyObject *s)
{
	double x;
	double y;
	if (! TwoFloatsFromVector2D(s, &x, &y)) {
		PyErr_SetString(PyExc_TypeError, "Subtrahend must be vector-like");
		return NULL;
	}
	Vector2D *result = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	result->x = self->x - x;
	result->y = self->y - y;
	return (PyObject *)result;
}

static PyObject *
Vector2D_mul(Vector2D *self, PyObject *i)
{
	if (! PyNumber_Check(i)) {
		PyErr_SetString(PyExc_TypeError, "Multiplicand must be a scalar");
		return NULL;
	}
	double d = PyFloat_AsDouble(i);
	Vector2D *result = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	result->x = self->x * d;
	result->y = self->y * d;
	return (PyObject *)result;
}

static PyObject *
Vector2D_classic_div(Vector2D *self, PyObject *i)
{
	if (! PyNumber_Check(i)) {
		PyErr_SetString(PyExc_TypeError, "Divisor must be a scalar");
		return NULL;
	}
	double d = PyFloat_AsDouble(i);
	Vector2D *result = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	result->x = self->x / d;
	result->y = self->y / d;
	return (PyObject *)result;
}

static PyObject *
Vector2D_neg(Vector2D *self)
{
	Vector2D *result = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	result->x = -self->x;
	result->y = -self->y;
	return (PyObject *)result;
}

static PyObject *
Vector2D_pos(Vector2D *self)
{
	Vector2D *result = (Vector2D *)Vector2D_new(&Vector2D_Type, NULL, NULL);
	result->x = +self->x;
	result->y = +self->y;
	return (PyObject *)result;
}

static PyNumberMethods Vector2D_as_number = {
    (binaryfunc)Vector2D_add,        /*nb_add*/
    (binaryfunc)Vector2D_sub,        /*nb_subtract*/
    (binaryfunc)Vector2D_mul,        /*nb_multiply*/
    (binaryfunc)Vector2D_classic_div, /*nb_divide*/
    0,//(binaryfunc)Vector2D_mod,        /*nb_remainder*/
    0,//(binaryfunc)Vector2D_divmod,     /*nb_divmod*/
    0,//(ternaryfunc)Vector2D_pow,       /*nb_power*/
    (unaryfunc)Vector2D_neg,         /*nb_negative*/
    (unaryfunc)Vector2D_pos,         /*nb_positive*/
    0,//(unaryfunc)Vector2D_abs,         /*nb_absolute*/
    0,//(inquiry)Vector2D_nonzero,       /*nb_nonzero*/
    0,//(unaryfunc)Vector2D_invert,      /*nb_invert*/
    0,//(binaryfunc)Vector2D_lshift,     /*nb_lshift*/
    0,//(binaryfunc)Vector2D_rshift,     /*nb_rshift*/
    0,//(binaryfunc)Vector2D_and,        /*nb_and*/
    0,//(binaryfunc)Vector2D_xor,        /*nb_xor*/
    0,//(binaryfunc)Vector2D_or,         /*nb_or*/
    0,//Vector2D_coerce,                 /*nb_coerce*/
    0,//(unaryfunc)Vector2D_int,         /*nb_int*/
    0,//(unaryfunc)Vector2D_long,        /*nb_long*/
    0,//(unaryfunc)Vector2D_float,       /*nb_float*/
    0,//(unaryfunc)Vector2D_oct,         /*nb_oct*/
    0,//(unaryfunc)Vector2D_hex,         /*nb_hex*/
    0,                          /*nb_inplace_add*/
    0,                          /*nb_inplace_subtract*/
    0,                          /*nb_inplace_multiply*/
    0,                          /*nb_inplace_divide*/
    0,                          /*nb_inplace_remainder*/
    0,                          /*nb_inplace_power*/
    0,                          /*nb_inplace_lshift*/
    0,                          /*nb_inplace_rshift*/
    0,                          /*nb_inplace_and*/
    0,                          /*nb_inplace_xor*/
    0,                          /*nb_inplace_or*/
    0,//(binaryfunc)Vector2D_div,        /* nb_floor_divide */
    0,//(binaryfunc)Vector2D_true_divide, /* nb_true_divide */
    0,                          /* nb_inplace_floor_divide */
    0,                          /* nb_inplace_true_divide */
    0,//(unaryfunc)Vector2D_int,         /* nb_index */
};

static Py_ssize_t
Vector2D_sq_length(Vector2D *self)
{
	return SEQ_LENGTH;
}

static PyObject *
Vector2D_sq_item(Vector2D *self, Py_ssize_t i)
{
	if (i < 0 || i >= SEQ_LENGTH) {
		PyErr_SetString(PyExc_IndexError, "vector index out of range");
		return NULL;
	}
	else if (i == 0) {
		return Vector2D_getX(self, NULL);
		//return (PyObject *)PyFloat_FromDouble(((Vector2D *)obj)->x);
	}
	else {
		return Vector2D_getY(self, NULL);
		//return (PyObject *)PyFloat_FromDouble(((Vector2D *)obj)->y);
	}
}

static int
Vector2D_sq_ass_item(Vector2D *self, Py_ssize_t i, PyObject *v){
	//double d = PyFloat_AsDouble(v);
	if (i < 0 || i >= SEQ_LENGTH) {
		PyErr_SetString(PyExc_IndexError, "vector index out of range");
		return -1;
	}
	else if (i == 0) {
		return Vector2D_setX(self, v, NULL);
		//((Vector2D *)obj)->x = d;
		//return 0;
	}
	else {
		return Vector2D_setY(self, v, NULL);
		//((Vector2D *)obj)->y = d;
		//return 0;
	}
}

static PySequenceMethods Vector2D_as_sequence = {
	(lenfunc)Vector2D_sq_length,		/* __len__ */
	0,//(binaryfunc)Vector2D_sq_concat	/* __add__ */
	0,//(ssizeargfunc)Vector2D_sq_repeat	/* __mul__ */
	(ssizeargfunc)Vector2D_sq_item,		/* __getitem__ */
	0,//(ssizesizeargfunc)Vector2D_sq_slice,	/* slice */
	(ssizeobjargproc)Vector2D_sq_ass_item,	/* __setitem__ */
	0,//(ssizessizeobjargproc)Vector2D_sq_ass_slice		/* slice assign */
	0,//(objobjproc)Vector2D_sq_contains,	/* x in o */
	0,//(binaryfunc)Vector2D_inplace_concat
	0,//(ssizeargfunc)Vector2D_inplace_repeat
};

static PyTypeObject Vector2D_Type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyVarObject_HEAD_INIT(NULL, 0)
    "vector.Vector2D",             /*tp_name*/
    sizeof(Vector2D),          /*tp_basicsize*/
    sizeof(double), //sizeof(long)?             /*tp_itemsize*/
    /* methods */
    (destructor)Vector2D_dealloc, /*tp_dealloc*/
    0,                          /*tp_print*/
    0,						/*tp_getattr*/
    0,					/*tp_setattr*/
    (cmpfunc)Vector2D_compare,                          /*tp_compare*/
    (reprfunc)Vector2D_repr,                          /*tp_repr*/
    &Vector2D_as_number,                          /*tp_as_number*/
    &Vector2D_as_sequence,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                      /*tp_call*/
    (reprfunc)Vector2D_repr,                      /*tp_str*/
    0,                      /*tp_getattro*/
    0,                      /*tp_setattro*/
    0,                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_CHECKTYPES,     /*tp_flags*/
    0,                      /*tp_doc*/
    0,                      /*tp_traverse*/
    0,                      /*tp_clear*/
    0,                      /*tp_richcompare*/
    0,                      /*tp_weaklistoffset*/
    0,                      /*tp_iter*/
    0,                      /*tp_iternext*/
    Vector2D_methods,                      /*tp_methods*/
    0,//Vector2D_members,	/*tp_members*/
    Vector2D_getsetters,                      /*tp_getset*/
    0,                      /*tp_base*/
    0,                      /*tp_dict*/
    0,                      /*tp_descr_get*/
    0,                      /*tp_descr_set*/
    0,                      /*tp_dictoffset*/
    (initproc)Vector2D_init,                      /*tp_init*/
    0,                      /*tp_alloc*/
    Vector2D_new,                      /*tp_new*/
    0,                      /*tp_free*/
    0,                      /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/* Function of two integers returning integer */

PyDoc_STRVAR(vector_foo_doc,
"foo(i,j)\n\
\n\
Return the sum of i and j.");

static PyObject *
vector_foo(PyObject *self, PyObject *args)
{
    long i, j;
    long res;
    if (!PyArg_ParseTuple(args, "ll:foo", &i, &j))
        return NULL;
    res = i+j; /* XXX Do something here */
    return PyInt_FromLong(res);
}

/* Function of no arguments returning new Vector2D object */
/*
static PyObject *
vector_new(PyObject *self, PyObject *args)
{
    Vector2D *rv;

    if (!PyArg_ParseTuple(args, ":new"))
        return NULL;
    rv = newVector2D(args);
    if (rv == NULL)
        return NULL;
    return (PyObject *)rv;
}
*/

/* Example with subtle bug from extensions manual ("Thin Ice"). */

/*
static PyObject *
vector_bug(PyObject *self, PyObject *args)
{
    PyObject *list, *item;

    if (!PyArg_ParseTuple(args, "O:bug", &list))
        return NULL;

    item = PyList_GetItem(list, 0);
    // Py_INCREF(item);
    PyList_SetItem(list, 1, PyInt_FromLong(0L));
    PyObject_Print(item, stdout, 0);
    printf("\n");
    // Py_DECREF(item);

    Py_INCREF(Py_None);
    return Py_None;
}
*/


/* ---------- */

/* List of functions defined in the module */

static PyMethodDef vector_methods[] = {
    {"foo",             vector_foo,         METH_VARARGS,
        vector_foo_doc},
//    {"bug",             vector_bug,         METH_VARARGS,
//        PyDoc_STR("bug(o) -> None")},
    {NULL,              NULL}           /* sentinel */
};

PyDoc_STRVAR(module_doc,
"This is a template module just for instruction.");

/* Initialization function for the module (*must* be called initvector) */

PyMODINIT_FUNC
initvector(void)
{
    PyObject *m;

    /* Create the module and add the functions */
    m = Py_InitModule3("vector", vector_methods, module_doc);
    if (m == NULL)
        return;

    /* Add some symbolic constants to the module */
    if (ErrorObject == NULL) {
        ErrorObject = PyErr_NewException("vector.error", NULL, NULL);
        if (ErrorObject == NULL)
            return;
    }
    Py_INCREF(ErrorObject);
    PyModule_AddObject(m, "error", ErrorObject);

	/* Add Vector2D */
    /* Finalize the type object including setting type of the new type
     * object; doing it here is required for portability, too. */
	if (PyType_Ready(&Vector2D_Type) < 0)
		return;
	PyModule_AddObject(m, "Vector2D", (PyObject *)&Vector2D_Type);
}

