---
sd_hide_title: true
---

# Overview

::::{grid}
:reverse:
:gutter: 3 4 4 4
:margin: 1 2 1 2

:::{grid-item}
:columns: 12 4 4 4

```{image} _static/logo-square.svg
:width: 200px
:class: sd-m-auto
```

:::

:::{grid-item}
:columns: 12 8 8 8
:child-align: justify
:class: sd-fs-5

```{rubric} Truss - Containers for serving Machine Learning Models
```

```{button-ref} SUMMARY
:ref-type: doc
:color: primary
:class: sd-rounded-pill

go to summary
```


A Truss is a context for building a container for serving predictions from a
model. Trusses are designed to work seamlessly with in-memory models from
supported model frameworks while maintaining the ability to serve predictions
for more complex scenarios. Trusses can be created local to the environment of
the client for introspection and any required debugging and then when ready,
uploaded in our serving environment or onto another container serving platform


:::

::::

```{toctree}
:hidden:
summary.md
```

```{toctree}
:hidden:
:caption: Guides

tutorials/creating-a-simple-truss
```

```{toctree}
:hidden:
:caption: Reference

source/truss.rst
```
