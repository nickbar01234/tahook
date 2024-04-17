import pygame as pg
from .styles import STYLE
from ..type.aliases import *


def create_prompt(screen: pg.Surface, prompt: str, margin: tuple[int, int]):
    font = STYLE["font"]["title"]
    text = font.render(prompt, True, "black")
    rect = text.get_rect()
    rect.midtop = screen.get_rect().midtop
    rect = rect.move(*margin)
    screen.blit(text, rect)


def create_textbox(screen: pg.Surface, dimension: tuple[int, int] = (512, 64), border: int = 3):
    textbox_border = pg.Rect(0, 0, *dimension)
    textbox_border.center = screen.get_rect().center
    left_x, left_y = textbox_border.topleft
    textbox = pg.Rect(
        0, 0, dimension[0] - border * 2, dimension[1] - border * 2)
    textbox.topleft = (left_x + border, left_y + border)
    return textbox, textbox_border


def create_submit_box():
    dist_from_corner = STYLE["width"] // 40
    box_topright = STYLE["width"] - \
        dist_from_corner, dist_from_corner
    width, height = STYLE["width"] // 15, STYLE["height"] // 15
    box = pg.Rect(0, 0, width, height)
    box.topright = box_topright

    return box


def create_button(screen: pg.Surface, margin: tuple[int, int]):
    border = 3
    width, height = 512, 64
    center_x, center_y = screen.get_rect().center
    textbox_border = pg.Rect(0, 0, width, height)
    textbox_border.center = (center_x, center_y)
    textbox_border = textbox_border.move(*margin)
    left_x, left_y = textbox_border.topleft
    textbox = pg.Rect(0, 0, width - border * 2, height - border * 2)
    textbox.topleft = (left_x + border, left_y + border)
    return textbox, textbox_border


def draw_submit_box(screen: pg.Surface, color, submit_box: pg.Rect):
    pg.draw.rect(screen, color, submit_box)
    # TODO: hardcoding it to start game for now
    submit_text_surface = STYLE["font"]["text"].render(
        "Start Game", True, (0, 0, 0))
    screen.blit(submit_text_surface, (submit_box.x + 10,
                                      submit_box.y + submit_box.height // 2 - 12))


def draw_leadersboard(screen: pg.Surface, leadersboard: LeadersBoard, ref_rect: pg.Rect):
    for idx, (name, n_questions) in enumerate(leadersboard):
        text = STYLE["font"]["text"].render(
            f"{name}: {n_questions}", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.midtop = ref_rect.midbottom
        text_rect.top = ref_rect.bottom
        text_rect = text_rect.move(0, ref_rect.height + idx * 32)
        screen.blit(text, text_rect)
