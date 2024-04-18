from time import sleep
from datetime import datetime
import logging
import pygame as pg
from .abstract_scene import AbstractScene
from .scene_state import SceneState
from .styles import STYLE
from ..solution.multiple_choice_solution_builder import MultipleChoiceSolutionBuilder
from . import utils
# from ..state.player_state import PlayerState
# from ..network import Network

logger = logging.getLogger()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


class QuestionScene(AbstractScene):
    def start_scene(self):
        # Now initialize the questions when starting the scene
        self.q_idx = 0
        self.num_questions = len(self.get_player_state().get_questions())
        self.curr_question = self.get_player_state().get_questions()[0]
        self.curr_options = self.curr_question.get_options()
        self.selected = set()
        self.boxes, self.box_borders = self.__create_options_boxes()
        self.submit_box, self.submit_box_text, self.submit_text_surface = self.get_utils(
        ).create_submit_box()

        # TODO: ensure the player selects at least one option
        # TODO: add a box that encloses the option boxes

        self.get_player_state().set_init_time()

        while True:
            for event in pg.event.get():
                self.handle_quit(event)
                match event.type:
                    case pg.MOUSEBUTTONDOWN:
                        if self.submit_box.collidepoint(event.pos):
                            # note: a janky way of detecting all questions have been answered (we can definitely change this later)
                            if not self.__submit():
                                delta = datetime.now() - self.get_player_state().get_init_time()
                                self.get_network().send_elapsed_time(delta.total_seconds())
                                return SceneState.PLAYER_WAIT_END_ROOM
                            continue

                        # update selection
                        for option, box in zip(self.curr_options, self.boxes):
                            if box.collidepoint(event.pos):
                                if option in self.selected:
                                    self.selected.remove(option)
                                else:
                                    self.selected.add(option)

            self.get_screen().fill("white")
            question_rect = self.curr_question.draw(self.get_screen())
            utils.draw_leadersboard(
                self.get_screen(), self.get_player_state().get_leadersboard(), question_rect)

            self.get_utils().draw_submit_box(
                self.submit_box, self.submit_box_text, self.submit_text_surface)

            # draw all options
            self.__draw_options()

            pg.display.flip()

    # move to the next question
    def __submit(self):
        user_solution = MultipleChoiceSolutionBuilder(self.selected).build()
        correctness = self.curr_question.verify(user_solution)
        self.__draw_correctness(correctness)
        self.get_player_state().set_progress(correctness)
        self.get_network().update_progress(self.get_player_state().get_progress())

        # update scene states
        self.q_idx += 1
        if self.num_questions == self.q_idx:
            return False

        self.curr_question = self.get_player_state().get_questions()[
            self.q_idx]
        self.curr_options = self.curr_question.get_options()
        self.selected = set()
        self.boxes, self.box_borders = self.__create_options_boxes()

        return True

    def __draw_correctness(self, correctness):
        text = STYLE["font"]["title"].render(
            f"Your answer was {correctness}!", True, (0, 0, 0))
        rect = text.get_rect()
        rect.center = self.get_screen().get_rect().center
        self.get_screen().fill("white")
        self.get_screen().blit(text, rect)
        pg.display.flip()
        sleep(1)

    def __draw_options(self):
        for i, (option, box) in enumerate(zip(self.curr_options, self.boxes)):
            selected = option in self.selected
            color_scheme = STYLE["box_colors"][i % len(STYLE["box_colors"])]
            pg.draw.rect(self.get_screen(
            ), color_scheme["active"] if selected else color_scheme["default"], box)
            text_surface = STYLE["font"]["answer"].render(
                option, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.center = box.center
            self.get_screen().blit(text_surface, text_rect)

    # def __create_submit_box(self):
    #     dist_from_corner = STYLE["width"] // 40
    #     box_topright = STYLE["width"] - \
    #         dist_from_corner, dist_from_corner
    #     width, height = STYLE["width"] // 15, STYLE["height"] // 15
    #     box = pg.Rect(0, 0, width, height)
    #     box.topright = box_topright

    #     return box

    def __create_options_boxes(self):
        boxes, box_borders = [], []

        # spacing between edge of screen and border of options zone that holds all options
        container = pg.Rect(0, 0, STYLE["width"] * 0.9, STYLE["height"] * 0.6)
        container.top = self.get_screen().get_rect().centery
        container.centerx = self.get_screen().get_rect().centerx

        margin_x, margin_y = 16, 32
        width, height = container.width // 2, 100
        row = 0
        for idx in range(len(self.curr_options)):
            box = pg.Rect(container.left + (idx % 2) * width + margin_x,
                          container.top + (row * (height + margin_y)), width - margin_x * 2, height)
            boxes.append(box)
            if idx % 2 != 0:
                row += 1

        return boxes, box_borders
