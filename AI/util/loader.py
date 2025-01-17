import json
from os import listdir, path
from pathlib import Path
from typing import List
import pickle

from betterproto import Casing

from data.proto import Frame
from data.game import Game
from util.attr_dict import AttrDict

from multiprocessing import Pool

BASE_PATH = Path(path.join(path.dirname(__file__), "..")).resolve()
RECORDINGS_PATH = path.join(BASE_PATH, "recordings")

def deserialize_gymbag(file_path: str) -> List[Frame]:
    frames = []

    with open(file_path, "rb") as file:
        data = file.read()
        index = 0

        while index < len(data):
            length = int.from_bytes(data[index:index+4], "little")
            index += 4

            frame = Frame()
            frame.parse(data[index:index+length])
            index += length

            frames.append(frame)

    return frames


def save_processed_game(file_path: str, game: Game):
    Path(path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    # with open(file_path, "w") as file:
    #     # Snake casing matches the dataclasses, and we need to include default values cuz otherwise they are not included and raise an error when accessing
    #     json.dump([f.to_dict(casing=Casing.SNAKE, include_default_values=True) for f in frames], file)
    # save pickled game data
    with open(file_path, "wb") as file:
        pickle.dump(game, file)


def load_processed_game(file_path: str) -> Game:
    with open(file_path, "r") as file:
        # we don't convert the loaded dictionaries to actual Frame objects to improve load time
        # instead we wrap it in an AttrDict which allows dict.attribute access by forwarding it to dict["attribute"]
        #return [AttrDict(f) for f in json.load(file)]  # type: ignore
        return pickle.load(file)
    
def load_game(file) -> Game:
    if file.endswith(".gymbag2"):
        file_path = path.join(RECORDINGS_PATH, file)
        
        # load the game, calculate number of possible frame sequence pairings
        # return decoded file path, number of possible frame sequence pairings
        # in the dataset we can figure out how to load it

        decoded_file_path = path.join(RECORDINGS_PATH, "decoded", path.splitext(file)[0] + ".pickle")
        if path.exists(decoded_file_path):
            print(f"Loading: {path.relpath(decoded_file_path, BASE_PATH)}")
            game = load_processed_game(decoded_file_path)
        else:
            print(f"Parsing: {path.relpath(file_path, BASE_PATH)}")
            frames = deserialize_gymbag(file_path)
            print(f"Updating game data")
            game = Game(frames)
            print(f"Saving: {path.relpath(decoded_file_path, BASE_PATH)}")
            save_processed_game(decoded_file_path, game)

        return game


def read_all_recordings() -> List[Game]:
    print("Loading recordings from disk... (this may take a bit)")

    result = listdir(RECORDINGS_PATH)
    with Pool(20) as p:
        result = p.map(load_game, result)

    print("Done loading recordings")

    return result
