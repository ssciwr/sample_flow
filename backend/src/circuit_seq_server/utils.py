from __future__ import annotations
from typing import Optional
import datetime
import pathlib
from circuit_seq_server.logger import get_logger
import string
import math
from Bio import SeqIO
import snapgene_reader
from itsdangerous.url_safe import URLSafeSerializer

logger = get_logger("CircuitSeqServer")


def encode_activation_token(email: str, secret_key: str) -> str:
    ss = URLSafeSerializer(secret_key, salt="activate")
    return ss.dumps(email)


def decode_activation_token(token: str, secret_key: str) -> Optional[str]:
    ss = URLSafeSerializer(secret_key, salt="activate")
    one_week_in_secs = 60 * 60 * 24 * 7
    try:
        email = ss.loads(token, max_age=one_week_in_secs)
    except Exception as e:
        logger.warn(f"Invalid or expired activation token: {e}")
        return None
    return email


def get_start_of_week(current_date: Optional[datetime.date] = None) -> datetime.date:
    if current_date is None:
        current_date = datetime.date.today()
    year, week, day = current_date.isocalendar()
    return datetime.date.fromisocalendar(year, week, 1)


def get_primary_key(
    year: int, week: int, current_count: int, n_rows: int, n_cols: int
) -> Optional[str]:
    max_samples = n_rows * n_cols
    row_labels = string.ascii_uppercase
    if current_count >= max_samples:
        return None

    i_row = math.floor(current_count / n_cols)
    i_col = current_count % n_cols
    yy = year % 100
    return f"{yy:02d}_{week:02d}_{row_labels[i_row]}{i_col + 1}"


def _guess_seqio_format(filename: str):
    ext = pathlib.Path(filename).suffix
    if ext in [".gb", ".gbk"]:
        return "genbank"
    elif ext in [".dna"]:
        return "snapgene"
    elif ext in [".embl"]:
        return "embl"
    return "fasta"


def parse_seq_to_fasta(
    input_file: pathlib.Path, output_file: str, original_filename: str
) -> Optional[str]:
    try:
        seqio_format = _guess_seqio_format(original_filename)
        logger.info(f"Parsing file {input_file} as {seqio_format}")
        record = next(SeqIO.parse(input_file, seqio_format).records)
        logger.info(f"  - id: {record.id}")
        logger.info(f"  - desc: {record.description}")
        if seqio_format == "snapgene":
            logger.info("Parsing snapgene file with snapgene_reader")
            try:
                d = snapgene_reader.snapgene_file_to_dict(input_file)
                notes = d.get("notes")
                if notes is not None:
                    logger.info("  -> found notes")
                    custom_id = notes.get("CustomMapLabel")
                    if custom_id is not None:
                        logger.info(
                            f"    -> using CustomMapLabel '{custom_id}' as record id"
                        )
                        record.id = custom_id
                    custom_desc = notes.get("Description")
                    if custom_desc is not None:
                        logger.info(
                            f"    -> using Description '{custom_desc}' as record description"
                        )
                        record.description = custom_desc
            except Exception as e:
                logger.warn(f"snapgene_reader error: {e}")
        if seqio_format == "fasta":
            reference_sequence_description = record.description
        else:
            reference_sequence_description = record.id
        logger.info(f"Writing fasta file to {output_file}")
        SeqIO.write(record, output_file, "fasta")
    except Exception as e:
        logger.info(f"Failed to parse file: {e}")
        return None
    return reference_sequence_description
