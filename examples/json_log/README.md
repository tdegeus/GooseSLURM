# json_log

> **Disclaimer**
> 
> This script is meant as an example, it comes with absolutely no warranty.
> 
>   (c - [MIT](../../LICENSE)) T.W.J. de Geus (Tom) | tom@geus.me | www.geus.me | [github.com/tdegeus/GooseSLURM](https://github.com/tdegeus/GooseSLURM)

This example is an extension to [tempdir](../tempdir). It additionally writes a log-file in the `submitdir` (on the head node) when the job is submitted. This file, [job.slurm.json](job.slurm.json), is formatted using JSON to facilitate (automatic) readability. In particular it can also be read by [Gcopy](../../bin/Gcopy), which can automatically copy files from the temporary directory on the compute node, back to the head node. This is exactly what is done when the job terminates, but this allows you to do also it before the job terminates.
