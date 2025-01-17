# This code is part of Qiskit.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Utilities for working with IBM Quantum backends."""

from typing import List, Optional, Dict, Union

import dateutil.parser

from ..backendreservation import BackendReservation
from ..utils.converters import utc_to_local


def convert_reservation_data(
    raw_reservations: List, backend_name: Optional[str] = None
) -> List[BackendReservation]:
    """Convert a list of raw reservation data to ``BackendReservation`` objects.

    Args:
        raw_reservations: Raw reservation data.
        backend_name: Name of the backend.

    Returns:
        A list of ``BackendReservation`` objects.
    """
    reservations = []
    for raw_res in raw_reservations:
        creation_datetime = raw_res.get("creationDate", None)
        creation_datetime = (
            utc_to_local(creation_datetime) if creation_datetime else None
        )
        backend_name = backend_name or raw_res.get("backendName", None)
        reservations.append(
            BackendReservation(
                backend_name=backend_name,
                start_datetime=utc_to_local(raw_res["initialDate"]),
                end_datetime=utc_to_local(raw_res["endDate"]),
                mode=raw_res.get("mode", None),
                reservation_id=raw_res.get("id", None),
                creation_datetime=creation_datetime,
                hub_info=raw_res.get("hubInfo", None),
            )
        )
    return reservations


def decode_pulse_defaults(defaults: Dict) -> None:
    """Decode pulse defaults data.

    Args:
        defaults: A ``PulseDefaults`` in dictionary format.
    """
    for item in defaults["pulse_library"]:
        _decode_pulse_library_item(item)

    for cmd in defaults["cmd_def"]:
        if "sequence" in cmd:
            for instr in cmd["sequence"]:
                _decode_pulse_qobj_instr(instr)


def decode_backend_properties(properties: Dict) -> None:
    """Decode backend properties.

    Args:
        properties: A ``BackendProperties`` in dictionary format.
    """
    properties["last_update_date"] = dateutil.parser.isoparse(
        properties["last_update_date"]
    )
    for qubit in properties["qubits"]:
        for nduv in qubit:
            nduv["date"] = dateutil.parser.isoparse(nduv["date"])
    for gate in properties["gates"]:
        for param in gate["parameters"]:
            param["date"] = dateutil.parser.isoparse(param["date"])
    for gen in properties["general"]:
        gen["date"] = dateutil.parser.isoparse(gen["date"])


def decode_backend_configuration(config: Dict) -> None:
    """Decode backend configuration.

    Args:
        config: A ``QasmBackendConfiguration`` or ``PulseBackendConfiguration``
            in dictionary format.
    """
    config["online_date"] = dateutil.parser.isoparse(config["online_date"])

    if "u_channel_lo" in config:
        for u_channle_list in config["u_channel_lo"]:
            for u_channle_lo in u_channle_list:
                u_channle_lo["scale"] = _to_complex(u_channle_lo["scale"])


def _to_complex(value: Union[List[float], complex]) -> complex:
    """Convert the input value to type ``complex``.

    Args:
        value: Value to be converted.

    Returns:
        Input value in ``complex``.

    Raises:
        TypeError: If the input value is not in the expected format.
    """
    if isinstance(value, list) and len(value) == 2:
        return complex(value[0], value[1])
    elif isinstance(value, complex):
        return value

    raise TypeError("{} is not in a valid complex number format.".format(value))


def _decode_pulse_library_item(pulse_library_item: Dict) -> None:
    """Decode a pulse library item.

    Args:
        pulse_library_item: A ``PulseLibraryItem`` in dictionary format.
    """
    pulse_library_item["samples"] = [
        _to_complex(sample) for sample in pulse_library_item["samples"]
    ]


def _decode_pulse_qobj_instr(pulse_qobj_instr: Dict) -> None:
    """Decode a pulse Qobj instruction.

    Args:
        pulse_qobj_instr: A ``PulseQobjInstruction`` in dictionary format.
    """
    if "val" in pulse_qobj_instr:
        pulse_qobj_instr["val"] = _to_complex(pulse_qobj_instr["val"])
    if "parameters" in pulse_qobj_instr and "amp" in pulse_qobj_instr["parameters"]:
        pulse_qobj_instr["parameters"]["amp"] = _to_complex(
            pulse_qobj_instr["parameters"]["amp"]
        )
