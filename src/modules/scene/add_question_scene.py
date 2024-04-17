import sys
import random
import pygame as pg
import pyperclip
from .abstract_scene import AbstractScene
from .scene_state import SceneState
from .styles import STYLE
from .utils import Utils
from ..type.aliases import *
# from ..state.player_state import PlayerState
# from ..network import Network


class AddQuestionScene(AbstractScene):
    def __init__(self, screen: pg.Surface, player_state, network):
        super().__init__(screen, player_state, network)

        self.questions: list[Question] = []
        self.question_description = ""
        self.utils = Utils(self.get_screen())
        self.__create_submit_box()
        self.__create_add_box()
        self.__create_prompt_with_inputbox()

    def start_scene(self):
        # TODO(nickbar01234) - Need to extract into a input class
        clock = pg.time.Clock()
        active = False
        filled = False
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit(0)

                if event.type == pg.MOUSEBUTTONDOWN:
                    active = self.question_box.collidepoint(event.pos)

                    if self.submit_box.collidepoint(event.pos):
                        # TODO finish and submit
                        pass

                    elif self.add_box.collidepoint(event.pos):
                        # TODO add next question
                        pass

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        print("Question added: ", question)
                        filled = True
                    elif event.key == pg.K_v and (event.mod & pg.KMOD_CTRL or event.mod & pg.KMOD_META):
                        self.question_description = pyperclip.paste()
                    elif event.key == pg.K_BACKSPACE:
                        self.question_description = self.question_description[:-1]
                    else:
                        self.question_description += event.unicode

            self.get_screen().fill("white")
            self.__draw_buttons()
            self.__draw_question_prompt(active, filled)

            padding_x, padding_y = 10, 12
            text_surface = STYLE["font"]["text"].render(
                self.question_description, True, (0, 0, 0))
            # TODO(nickbar01234) - Handle clip text
            self.get_screen().blit(text_surface, (self.question_box.x + padding_x,
                                                  self.question_box.y + self.question_box.height // 2 - padding_y))

            pg.display.flip()
            clock.tick(STYLE["fps"])

    #
    # Protocols for state management & sending messages
    #

    def __add_question_description(self, question):
        self.questions.append(question)
        print("Question added: ", question)

    #
    # UI drawing & rendering
    #

    def __create_prompt_with_inputbox(self):
        self.prompt, self.question_box, self.question_box_border = self.utils.create_prompt_with_inputbox(
            "Add question description: ", (768, 64), font_style="question")

    def __draw_question_prompt(self, active: bool, filled: bool):
        self.get_screen().blit(*self.prompt)

        pg.draw.rect(self.get_screen(), pg.Color("#00FF00")
                     if filled else pg.Color("#8489FBFF") if active else "black", self.question_box_border)
        pg.draw.rect(self.get_screen(), "white", self.question_box)

    def __create_submit_box(self):
        self.submit_box, self.submit_box_text, self.submit_text_surface = self.utils.create_submit_box(
            "Finish and Submit")

    def __create_add_box(self):
        self.add_box, self.add_box_text, self.add_text_surface = self.utils.create_bottom_right_box(
            "Add")

    def __draw_buttons(self):
        self.utils.draw_submit_box(
            self.submit_box, self.submit_box_text, self.submit_text_surface)
        self.utils.draw_bottom_right_box(
            self.add_box, self.add_box_text, self.add_text_surface)

    def __submit(self):
        # logger.info("Referee submits questions")
        # TODO: broadcast the start game signal to all players
        print("Referee submits questions")
