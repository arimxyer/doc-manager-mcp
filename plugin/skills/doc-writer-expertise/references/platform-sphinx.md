# Sphinx Formatting Guide

Reference for Sphinx reStructuredText (RST) formatting.

## Directives

### Admonitions

```rst
.. note::
   This is a note.

.. warning::
   This is a warning.

.. danger::
   This is a danger alert.

.. tip::
   This is a helpful tip.

.. important::
   This is important information.

.. seealso::
   Related content here.
```

### Custom Admonition

```rst
.. admonition:: Custom Title

   Content of the custom admonition.
```

---

## Code Blocks

### Basic

```rst
.. code-block:: python

   def hello():
       print("Hello, World!")
```

### With Line Numbers

```rst
.. code-block:: python
   :linenos:

   def hello():
       print("Hello, World!")
```

### With Caption

```rst
.. code-block:: python
   :caption: example.py

   def hello():
       print("Hello, World!")
```

### Highlighting Lines

```rst
.. code-block:: python
   :emphasize-lines: 2,3

   def hello():
       message = "Hello"
       print(message)
```

### Include from File

```rst
.. literalinclude:: ../examples/sample.py
   :language: python
   :lines: 10-20
```

---

## Cross-References

### To Documents

```rst
See :doc:`/guides/installation` for setup instructions.
See :doc:`installation` for relative reference.
```

### To Sections

```rst
See :ref:`section-label` for details.

.. _section-label:

Section Title
-------------
```

### To Python Objects

```rst
See :func:`module.function_name` for the function.
See :class:`module.ClassName` for the class.
See :meth:`module.ClassName.method` for the method.
See :attr:`module.ClassName.attribute` for the attribute.
See :mod:`module` for the module.
See :exc:`module.ExceptionName` for the exception.
```

---

## Tables

### Simple Table

```rst
=====  =====  =====
Col 1  Col 2  Col 3
=====  =====  =====
A      B      C
D      E      F
=====  =====  =====
```

### Grid Table

```rst
+-------+-------+-------+
| Col 1 | Col 2 | Col 3 |
+=======+=======+=======+
| A     | B     | C     |
+-------+-------+-------+
| D     | E     | F     |
+-------+-------+-------+
```

### List Table

```rst
.. list-table:: Table Title
   :widths: 25 25 50
   :header-rows: 1

   * - Column 1
     - Column 2
     - Column 3
   * - Value 1
     - Value 2
     - Value 3
```

---

## Links

### External Links

```rst
`Link text <https://example.com>`_
```

### Named References

```rst
See the `Python docs`_ for more.

.. _Python docs: https://docs.python.org
```

### Internal Links

```rst
:doc:`/path/to/document`
:ref:`label-name`
```

---

## Images

### Basic Image

```rst
.. image:: ../images/screenshot.png
   :alt: Screenshot description
```

### With Options

```rst
.. image:: ../images/screenshot.png
   :alt: Screenshot description
   :width: 400px
   :align: center
```

### Figure with Caption

```rst
.. figure:: ../images/diagram.png
   :alt: Diagram description
   :width: 600px

   This is the figure caption.
```

---

## Function/Class Documentation

### Function

```rst
.. function:: process_data(data, options=None)

   Process the input data with optional configuration.

   :param data: Input data to process
   :type data: dict
   :param options: Optional configuration
   :type options: dict, optional
   :returns: Processed result
   :rtype: ProcessedData
   :raises ValueError: If data is invalid
```

### Class

```rst
.. class:: DataProcessor(config)

   Process data with configurable options.

   :param config: Processor configuration
   :type config: Config

   .. attribute:: status

      Current processor status.

      :type: str

   .. method:: process(data)

      Process the input data.

      :param data: Data to process
      :returns: Processed result
```

### Autodoc

```rst
.. autofunction:: module.function_name

.. autoclass:: module.ClassName
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: module
   :members:
```

---

## Versioning

### Version Added

```rst
.. versionadded:: 2.0
   New feature description.
```

### Version Changed

```rst
.. versionchanged:: 2.1
   Behavior change description.
```

### Deprecated

```rst
.. deprecated:: 2.0
   Use :func:`new_function` instead.
```

---

## Best Practices

1. **Use autodoc** for API documentation when possible
2. **Cross-reference** with proper roles (`:func:`, `:class:`, etc.)
3. **Use list-table** for complex tables
4. **Add version annotations** for changes
5. **Include type information** in parameter docs
6. **Use figures** for images that need captions
7. **Keep consistent indentation** (3 spaces standard)
