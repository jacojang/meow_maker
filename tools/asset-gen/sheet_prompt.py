"""Build a 3x2 sheet prompt: five framed animation frames of one activity in a single image."""

import re
import subprocess
import sys


def moment(act: str, frame: str) -> str:
    text = subprocess.run(["./scene_prompt.sh", act, frame], capture_output=True, text=True, check=True).stdout
    return re.search(r"Moment \d: [^.]*\.", text).group(0)


def build(act: str) -> str:
    base = subprocess.run(["./scene_prompt.sh", act, "a"], capture_output=True, text=True, check=True).stdout
    scene = re.search(r"Scene: (.*?) Moment \d", base).group(1)
    moments = " ".join(moment(act, f) for f in "abcde")
    return (
        "Create ONE image laid out as a 3 columns by 2 rows grid of equal square panels with equal wide gutters between them and an even outer margin, so that no panel touches or is cut off by the image edge, reading left to right then top to bottom. "
        "Panels 1 to 5 are five consecutive animation frames of the same short scene; panel 6 (bottom right) is left completely empty cream. "
        "Each panel has its own thin dark rounded border frame and the same plain flat warm cream background (#F6EBD9) with a faint floor line. "
        "Clean flat cel-shaded style with uniform medium-thick dark outlines, the same style as the references. "
        "In every panel the cat must be exactly the cat in the first reference image (identical markings: black head with white blaze, white chest and belly, two large black body patches, black tail, white paws, yellow eyes) "
        "and the woman must be exactly the girl in the second reference image (long dark brown hair, blue and white striped t-shirt, navy slim pants, white sneakers). "
        "Keep the same camera distance, the same character size and the same positions on the floor in all five panels: the woman stays in exactly the same spot and the same sitting or standing position as in panel 1 and only her arms and expression change; the cat stays in the same area of the panel. Both characters are fully visible from head to toe in every panel, standing on the same floor line near the bottom of each panel, never cropped by the panel border. "
        f"Scene: {scene} {moments} Full figures in each panel with a clear margin, woman's head about 16% of the panel height. No text, no numbers."
    )


if __name__ == "__main__":
    print(build(sys.argv[1]))
