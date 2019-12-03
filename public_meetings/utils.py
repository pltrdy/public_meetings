import os
import pickle
import public_meetings


def load_meeting(path):
    """Load meeting from path
    """
    with open(path, 'rb') as f:
        return pickle.load(f)


def load_meetings(root=public_meetings.data_root,
                  ext=public_meetings.file_ext):
    """
        Load all meetings from `root` ending with `ext`

        Args:
            root(str): root meeting directory
            ext(str): file extension

        Returns:
            meetings(dict): a dictionnary {hash: meeting_data}
    """
    meetings = {}
    for filename in os.listdir(root):
        if not filename.endswith(ext):
            continue

        path = os.path.join(root, filename)
        h = filename.replace(ext, '')

        meetings[h] = load_meeting(path)
    return meetings
