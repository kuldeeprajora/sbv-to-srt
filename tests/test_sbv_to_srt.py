from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from sbv_to_srt import SBVConversionError, convert_file, convert_sbv_text_to_srt
from sbv_to_srt_gui import choose_unique_destination, collect_sbv_files


class ConversionTests(TestCase):
    def test_converts_multiline_subtitle(self) -> None:
        source = "0:00:01.5,0:00:03.250\nFirst line\nSecond line\n"

        result = convert_sbv_text_to_srt(source)

        self.assertEqual(
            result,
            "1\n00:00:01,500 --> 00:00:03,250\nFirst line\nSecond line\n",
        )

    def test_rejects_end_time_before_start_time(self) -> None:
        source = "0:00:04.000,0:00:03.000\nInvalid timing\n"

        with self.assertRaisesRegex(SBVConversionError, "end time is before start time"):
            convert_sbv_text_to_srt(source)

    def test_convert_file_reads_utf8_bom_and_writes_srt(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            folder = Path(temporary_directory)
            source = folder / "captions.sbv"
            source.write_text("\ufeff0:00:01.000,0:00:02.000\nHello\n", encoding="utf-8")

            destination = convert_file(source)

            self.assertEqual(destination, folder / "captions.srt")
            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                "1\n00:00:01,000 --> 00:00:02,000\nHello\n",
            )


class GuiHelperTests(TestCase):
    def test_collect_sbv_files_is_non_recursive_and_case_insensitive(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            folder = Path(temporary_directory)
            (folder / "b.SBV").write_text("", encoding="utf-8")
            (folder / "a.sbv").write_text("", encoding="utf-8")
            (folder / "ignore.txt").write_text("", encoding="utf-8")
            nested = folder / "nested"
            nested.mkdir()
            (nested / "nested.sbv").write_text("", encoding="utf-8")

            result = collect_sbv_files(folder)

            self.assertEqual([path.name for path in result], ["a.sbv", "b.SBV"])

    def test_unique_destination_adds_number_for_batch_collision(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "captions.srt"
            reserved: set[str] = set()

            first = choose_unique_destination(destination, reserved)
            second = choose_unique_destination(destination, reserved)

            self.assertEqual(first.name, "captions.srt")
            self.assertEqual(second.name, "captions_2.srt")
