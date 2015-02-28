from crc_nd.utils.test_io import WritesOutputFiles
from path import path

from ..utils import get_file_contents


class GetFileContentsTests(WritesOutputFiles):
    """
    Tests of the get_file_contents function.
    """

    @classmethod
    def setUpClass(cls):
        output_root = path(__file__).dirname() / 'output'
        cls.set_output_root(output_root)

    def create_test_file(self, filename, lines):
        file_path = self.get_output_dir() / filename
        file_path.write_lines(lines)

    def null_callback(self, filename):
        """
        A callback that does nothing with its filename argument
        """
        pass

    def test_0_filenames(self):
        """
        Test when an empty sequence of filenames is given.
        """
        file_contents = get_file_contents([], self.null_callback)
        self.assertEqual(file_contents, dict())

    def test_1_filename(self):
        """
        Test with a list of one filename.
        """
        self.initialize_output_dir()
        filename = 'foobar.txt'
        self.create_test_file(filename, LOREM_IPSUM)

        file_contents = get_file_contents([filename], self.null_callback, dir_path=self.get_output_dir())
        expected_contents = {
            filename : add_newlines(LOREM_IPSUM),
        }
        self.assertEqual(file_contents, expected_contents)

    def test_3_filenames(self):
        """
        Test with a list of 3 filenames.
        """
        self.initialize_output_dir()

        expected_contents = dict()
        for filename, file_contents in (
            ('lorem.txt', LOREM_IPSUM),
            ('sample_data.csv', SAMPLE_CSV_DATA),
            ('empty.dat', []),
        ):
            self.create_test_file(filename, file_contents)
            expected_contents[filename] = add_newlines(file_contents)

        file_contents = get_file_contents(expected_contents.keys(), self.null_callback, dir_path=self.get_output_dir())
        self.assertEqual(file_contents, expected_contents)


def add_newlines(lines):
    """
    Add newlines to a sequence of text lines.

    :return list: A new list with each line having a newline appended to it.
    """
    return [ line + '\n' for line in lines]


LOREM_IPSUM = (
    'Lorem ipsum dolor sit amet,',
    ' consectetur adipiscing elit,',
    ' sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
    'Ut enim ad minim veniam,',
    ' quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
    'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
    'Excepteur sint occaecat cupidatat non proident,',
    ' sunt in culpa qui officia deserunt mollit anim id est laborum.',
)


SAMPLE_CSV_DATA = (
    '1,1,0,1000',
    '1,1,3,480',
    '2,1,0,1000',
    '2,1,3,497',
    '3,1,0,1000',
    '3,1,3,450',
    '4,1,0,1000',
    '4,1,3,451',
    '5,1,0,1000',
    '5,1,3,463',
    '6,1,0,1000',
    '6,1,3,458',
    '7,1,0,1000',
    '7,1,3,483',
    '8,1,0,1000',
    '8,1,3,493',
    '9,1,0,1000',
    '9,1,3,457',
    '10,1,0,1000',
    '10,1,3,469',
    '11,1,0,1000',
    '11,1,3,445',
)
