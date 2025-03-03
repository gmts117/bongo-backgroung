import os
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image

def select_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="GIF 파일을 선택하세요", filetypes=[("GIF files", "*.gif")])

def select_directory():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="저장할 폴더를 선택하세요")

def get_screen_size():
    while True:
        try:
            width = int(input("너비 (픽셀): "))
            height = int(input("높이 (픽셀): "))
            if width > 0 and height > 0:
                return width, height
        except ValueError:
            pass
        print("올바른 숫자를 입력하세요.")

def get_gif_speed():
    while True:
        try:
            speed = int(input("프레임 간격(밀리초): "))
            if speed > 0:
                return speed
        except ValueError:
            pass
        print("올바른 숫자를 입력하세요.")

def get_position_ratio():
    while True:
        try:
            ratio = float(input("이미지를 배치할 높이 비율 (0.0 ~ 1.0): "))
            if 0.0 <= ratio <= 1.0:
                return ratio
        except ValueError:
            pass
        print("0과 1 사이의 값을 입력하세요.")

def get_width_ratio():
    while True:
        try:    
            ratio = float(input("이미지 너비 비율 (0.0 ~ 1.0): "))
            if 0.0 < ratio <= 1.0:
                return ratio
        except ValueError:
            pass
        print("0과 1 사이의 값을 입력하세요.")

def split_gif_frames(gif_path, temp_folder):
    frames = []
    with Image.open(gif_path) as img:
        frame = 0
        while True:
            frame_path = os.path.join(temp_folder, f"frame_{frame:03d}.png")
            img.save(frame_path, format="PNG")
            frames.append(frame_path)
            try:
                img.seek(frame + 1)
                frame += 1
            except EOFError:
                break
    return frames

def resize_and_place_image(background_size, image_path, output_path, position_ratio, width_ratio):
    background = Image.new("RGB", background_size, "white")
    image = Image.open(image_path).convert("RGBA")
    new_width = int(background_size[0] * width_ratio)
    scale_factor = new_width / image.width
    new_height = int(image.height * scale_factor)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    position_y = int(background_size[1] * position_ratio)
    position_x = (background_size[0] - new_width) // 2
    background.paste(resized_image, (position_x, position_y), resized_image)
    background.save(output_path, "PNG")

def create_gif(image_folder, output_path, duration):
    images = sorted([f for f in os.listdir(image_folder) if f.endswith(".png")])
    if not images:
        return False
    first_image = Image.open(os.path.join(image_folder, images[0]))
    frames = [Image.open(os.path.join(image_folder, img)) for img in images[1:]]
    first_image.save(output_path, save_all=True, append_images=frames, duration=duration, loop=0)
    first_image.close()
    for img in frames:
        img.close()
    return True

def main():
    print("GIF 배경화면 변환 프로그램")
    gif_path = select_file()
    if not gif_path:
        print("파일이 선택되지 않았습니다.")
        return
    output_folder = select_directory()
    if not output_folder:
        print("폴더가 선택되지 않았습니다.")
        return
    background_size = get_screen_size()
    gif_speed = get_gif_speed()
    position_ratio = get_position_ratio()
    width_ratio = get_width_ratio()
    
    with tempfile.TemporaryDirectory() as temp_folder:
        frames = split_gif_frames(gif_path, temp_folder)
        processed_folder = os.path.join(temp_folder, "processed")
        os.makedirs(processed_folder)
        for i, frame in enumerate(frames):
            output_path = os.path.join(processed_folder, f"frame_{i:03d}.png")
            resize_and_place_image(background_size, frame, output_path, position_ratio, width_ratio)
        final_gif_path = os.path.join(output_folder, "final_animated_background.gif")
        if create_gif(processed_folder, final_gif_path, gif_speed):
            print(f"GIF 생성 완료: {final_gif_path}")
        else:
            print("GIF 생성 실패")

if __name__ == "__main__":
    main()
