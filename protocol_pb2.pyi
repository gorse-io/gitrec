import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ()
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    labels: bytes
    comment: str
    subscribe: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, user_id: _Optional[str] = ..., labels: _Optional[bytes] = ..., comment: _Optional[str] = ..., subscribe: _Optional[_Iterable[str]] = ...) -> None: ...

class Item(_message.Message):
    __slots__ = ()
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    IS_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    item_id: str
    is_hidden: bool
    categories: _containers.RepeatedScalarFieldContainer[str]
    timestamp: _timestamp_pb2.Timestamp
    labels: bytes
    comment: str
    def __init__(self, namespace: _Optional[str] = ..., item_id: _Optional[str] = ..., is_hidden: _Optional[bool] = ..., categories: _Optional[_Iterable[str]] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., labels: _Optional[bytes] = ..., comment: _Optional[str] = ...) -> None: ...

class Feedback(_message.Message):
    __slots__ = ()
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    feedback_type: str
    user_id: str
    item_id: str
    value: float
    timestamp: _timestamp_pb2.Timestamp
    comment: str
    def __init__(self, namespace: _Optional[str] = ..., feedback_type: _Optional[str] = ..., user_id: _Optional[str] = ..., item_id: _Optional[str] = ..., value: _Optional[float] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., comment: _Optional[str] = ...) -> None: ...
