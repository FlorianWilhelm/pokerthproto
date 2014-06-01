# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from .pokerth_pb2 import PokerTHMessage

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

from IPython import embed


def makeSizeBytes(n):
    """
    Create a 4 bytes string that encodes the number ``n``.

    :param n: integer
    :return: 4 bytes string
    """
    return str(bytearray.fromhex(b'{:08x}'.format(n)))


def readSizeBytes(string):
    """
    Reads the 4 byte size-string and returns the size as integer.

    :param string: 4 byte size-string
    :return: integer
    """
    assert len(string) == 4
    return int(string.encode('hex'), 16)


def unpack(data):
    """
    Unpacks/Deserializes a PokerTH network messsage.

    :param data: data as string
    :return: PokerTHMessage object containing the message
    """
    size, data = readSizeBytes(data[:4]), data[4:]
    assert len(data) == size
    envelope = PokerTHMessage()
    envelope.ParseFromString(data)
    return envelope


def pack(envelope):
    """
    Packs/Serializes a PokerTHMessage to a data string.

    :param envelope: PokerTHMessage envelope
    :return: data as string
    """
    data = envelope.SerializeToString()
    size_bytes = makeSizeBytes(len(data))
    return size_bytes + data


def develop(envelope):
    """
    Remove the envelope from a message.

    :param envelope: PokerTHMessage ojbect that envelops a message
    :return: PokerTH message from the envelope
    """
    msg = [v for _, v in envelope.ListFields() if v != envelope.messageType]
    assert len(msg) == 1
    return msg[0]


def _getEnvelopeAttr(msg_name):
    """
    Get attribute name of an envelope for a given message name.

    :param msg_name: name of message
    :return: attribute name of message
    """
    return msg_name[0].lower() + msg_name[1:]


def _getMsgTypeAttr(msg_name):
    """
    Get the attribute name for the type of a message.

    :param msg_name: name of message
    :return: attribute name of message's type
    """
    return "Type_{}".format(msg_name)


def envelop(msg):
    """
    Put a message into an envelope.

    :param msg: PokerTH message object
    :return: message wrapped in an PokerTHMessage object
    """
    msg_name = msg.__class__.__name__
    envelope = PokerTHMessage()
    envelope_msg = getattr(envelope, _getEnvelopeAttr(msg_name))
    envelope_msg.MergeFrom(msg)
    msg_type = getattr(envelope, _getMsgTypeAttr(msg_name))
    setattr(envelope, 'messageType', msg_type)
    return envelope


def packEnvelop(msg):
    """
    Convenience function for pack and envelop.

    :param msg: message object
    :return: data message as string
    """
    return pack(envelop(msg))
