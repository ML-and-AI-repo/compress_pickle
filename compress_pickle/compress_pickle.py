# -*- coding: utf-8 -*-
"""
A thin wrapper of standard ``pickle`` with standard compression libraries
"""
import sys
import pickle
import io
from .utils import (
    validate_compression,
    preprocess_path,
    open_compression_stream,
    get_compression_write_mode,
    get_compression_read_mode,
)


__all__ = ["dump", "load", "dumps", "loads"]


def dump(
    obj,
    path,
    compression="infer",
    mode=None,
    protocol=-1,
    fix_imports=True,
    unhandled_extensions="raise",
    set_default_extension=True,
    **kwargs,
):
    r"""Dump the contents of an object to disk, to the supplied path, using a
    given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is
    opened as ``gzip.open`` and the desired content is dumped into the buffer
    using a normal ``pickle.dump`` call.

    Parameters
    ----------
    obj: any
        The object that will be saved to disk
    path: str
        The path to the file to which to dump ``obj``
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.compress_pickle.get_known_compressions`.
    mode: None or str (optional)
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to
        :func:`~compress_pickle.compress_pickle.get_compression_write_mode` to
        see the defaults.
    protocol: int (optional)
        Pickle protocol to use
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    set_default_extension: bool (optional)
        If ``True``, the default extension given the provided compression
        protocol is set to the supplied ``path``. Refer to
        :func:`~compress_pickle.compress_pickle.set_default_extensions` for
        more information.
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be "ignore" (use
        ".pkl"), "warn" (issue warning and use ".pkl") or "raise" (raise a
        ValueError).
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol.

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.
    """
    validate_compression(compression)
    path, compression, stream = preprocess_path(
        path,
        compression=compression,
        unhandled_extensions=unhandled_extensions,
        set_default_extension=set_default_extension,
    )
    if mode is None:
        mode = get_compression_write_mode(compression)

    io_stream, arch, arcname, must_close = open_compression_stream(
        path, compression, stream, mode, **kwargs
    )

    if arch is not None:
        try:
            if sys.version_info < (3, 6):
                buff = pickle.dumps(obj, protocol=protocol, fix_imports=fix_imports)
                arch.writestr(arcname, buff)
            else:
                pickle.dump(obj, io_stream, protocol=protocol, fix_imports=fix_imports)
        finally:
            if must_close:
                io_stream.close()
                arch.close()
    else:
        try:
            pickle.dump(obj, io_stream, protocol=protocol, fix_imports=fix_imports)
        finally:
            if must_close:
                io_stream.close()


def dumps(obj, compression=None, protocol=-1, fix_imports=True, **kwargs):
    r"""Dump the contents of an object to a byte string, using a
    given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is
    opened as ``gzip.open`` and the desired content is dumped into the buffer
    using a normal ``pickle.dump`` call.

    Parameters
    ----------
    obj: any
        The object that will be saved to disk
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.compress_pickle.get_known_compressions(False)`.
    protocol: int (optional)
        Pickle protocol to use
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol.

    """
    compression = validate_compression(compression, infer_is_valid=False)
    stream = io.BytesIO()
    dump(
        obj,
        path=stream,
        compression=compression,
        protocol=protocol,
        fix_imports=fix_imports,
        set_default_extension=False,
        **kwargs,
    )
    return stream.getvalue()


def load(
    path,
    compression="infer",
    mode=None,
    fix_imports=True,
    encoding="ASCII",
    errors="strict",
    set_default_extension=True,
    unhandled_extensions="raise",
    **kwargs,
):
    r"""Load an object from a file stored in disk, given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is opened
    as ``gzip.open`` and the desired content is loaded from the open buffer
    using a normal ``pickle.load`` call.

    Parameters
    ----------
    path: str
        The path to the file from which to load the ``obj``
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.compress_pickle.get_known_compressions`.
    mode: None or str (optional)
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to
        :func:`~compress_pickle.compress_pickle.get_compression_read_mode` to
        see the defaults.
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    encoding: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    errors: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    set_default_extension: bool (optional)
        If `True`, the default extension given the provided compression
        protocol is set to the supplied `path`. Refer to
        :func:`~compress_pickle.compress_pickle.set_default_extensions` for
        more information.
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be "ignore" (use
        ".pkl"), "warn" (issue warning and use ".pkl") or "raise" (raise a
        ValueError).
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol.

    Returns
    -------
    The unpickled object: any

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.
    """
    validate_compression(compression)
    path, compression, stream = preprocess_path(
        path,
        compression=compression,
        unhandled_extensions=unhandled_extensions,
        set_default_extension=set_default_extension,
    )
    if mode is None:
        mode = get_compression_read_mode(compression)

    io_stream, arch, arcname, must_close = open_compression_stream(
        path, compression, stream, mode, **kwargs
    )

    if arch is not None:
        try:
            output = pickle.load(
                io_stream, encoding=encoding, errors=errors, fix_imports=fix_imports
            )
        finally:
            if must_close:
                arch.close()
                io_stream.close()
    else:
        try:
            output = pickle.load(
                io_stream, encoding=encoding, errors=errors, fix_imports=fix_imports
            )
        finally:
            if must_close:
                io_stream.close()
    return output


def loads(
    data,
    compression,
    fix_imports=True,
    encoding="ASCII",
    errors="strict",
    set_default_extension=True,
    unhandled_extensions="raise",
    **kwargs,
):
    r"""Load an object from an input stream, uncompressing the contents with
    the given a compression protocol.

    Parameters
    ----------
    data: str
        The bytes that contain the object to load from
    compression: None or str
        The compression protocol to use. To see available compression
        protocols refer to
        :func:`~compress_pickle.compress_pickle.get_known_compressions`.
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    encoding: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    errors: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol.

    Returns
    -------
    The unpickled object: any

    Notes
    -----
    The compression is a mandatory argument and it cannot be inferred from the
    input stream parameter.
    """
    validate_compression(compression, infer_is_valid=False)
    with io.BytesIO(bytes(data)) as stream:
        return load(
            stream,
            compression=compression,
            fix_imports=fix_imports,
            encoding=encoding,
            errors=errors,
            **kwargs,
        )
