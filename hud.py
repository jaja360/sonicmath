import pygame

from game_state import DamageEffect, ScoreEffect, SpecialEffect, SpeedEffect, Status

HUD_BACKGROUND_COLOR = (18, 22, 32)
PANEL_COLOR = (27, 34, 48)
PANEL_BORDER_COLOR = (60, 82, 120)
PANEL_DIVIDER_COLOR = (78, 92, 116)
TEXT_COLOR = (235, 240, 250)
MUTED_TEXT_COLOR = (159, 176, 204)
QUESTION_COLOR = (255, 230, 140)
QUESTION_CORRECT_COLOR = (103, 220, 120)
INPUT_BACKGROUND_COLOR = (12, 15, 24)
INPUT_BORDER_COLOR = (90, 120, 170)
HEALTH_BACKGROUND_COLOR = (78, 24, 24)
HEALTH_FILL_COLOR = (67, 192, 94)
HEALTH_SHIELD_FILL_COLOR = (78, 196, 255)
STATUS_COLORS = {
    "normal": (67, 192, 94),
    "poisoned": (155, 89, 182),
    "burned": (231, 126, 35),
    "frozen": (52, 152, 219),
}
HUD_SPACING = 12
HUD_LEFT_PANEL_WIDTH = 560
HUD_RIGHT_PANEL_WIDTH = 220
HUD_CENTER_SECTION_GAP = 24
EFFECT_ROW_GAP = 14
EFFECT_COLUMN_GAP = 50
EFFECT_LABEL_GAP = 12
SPECIAL_LABELS = {
    SpecialEffect.DEBUFF_IMMUNE: "Debuff Immune",
    SpecialEffect.HEAL_BLOCKED: "Heal Blocked",
    SpecialEffect.BUFF_BLOCKED: "Buff Blocked",
    SpecialEffect.VISUAL_DEBUFF: "Hazards Dimmed",
}


class Hud:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.text_font = pygame.font.SysFont(None, 42)
        self.question_font = pygame.font.SysFont(None, 56)
        self.effect_font = pygame.font.SysFont(None, 30)

    def draw(self, screen, state):
        self.surface.fill(HUD_BACKGROUND_COLOR)

        left_rect = pygame.Rect(HUD_SPACING, HUD_SPACING, HUD_LEFT_PANEL_WIDTH, self.height - HUD_SPACING * 2)
        right_rect = pygame.Rect(
            self.width - HUD_SPACING - HUD_RIGHT_PANEL_WIDTH,
            HUD_SPACING,
            HUD_RIGHT_PANEL_WIDTH,
            self.height - HUD_SPACING * 2,
        )
        center_rect = pygame.Rect(
            left_rect.right + HUD_SPACING,
            HUD_SPACING,
            right_rect.left - left_rect.right - HUD_SPACING * 2,
            self.height - HUD_SPACING * 2,
        )

        section_width = (center_rect.width - 48 - HUD_CENTER_SECTION_GAP) // 2
        question_rect = pygame.Rect(
            center_rect.x + 24,
            center_rect.y + 18,
            section_width,
            center_rect.height - 36,
        )
        input_rect = pygame.Rect(
            question_rect.right + HUD_CENTER_SECTION_GAP,
            center_rect.y + 18,
            section_width,
            center_rect.height - 36,
        )

        self._draw_panel(left_rect)
        self._draw_panel(center_rect)
        self._draw_panel(right_rect)

        self._draw_health_bar(left_rect, state.health, state.next_hit_immune)
        self._draw_status(left_rect, state)
        self._draw_score(right_rect, state)
        self._draw_level(right_rect, state.level)

        self._draw_question(question_rect, state, state.is_answer_pending)
        self._draw_input(input_rect, state)

        screen.blit(self.surface, (0, 0))

    def _draw_panel(self, rect):
        pygame.draw.rect(self.surface, PANEL_COLOR, rect, border_radius=18)
        pygame.draw.rect(self.surface, PANEL_BORDER_COLOR, rect, width=2, border_radius=18)

    def _draw_label_value(self, label, value, x, y, value_color=TEXT_COLOR):
        label_surface = self.text_font.render(label, True, MUTED_TEXT_COLOR)
        value_surface = self.text_font.render(str(value), True, value_color)
        self.surface.blit(label_surface, (x, y))
        self.surface.blit(value_surface, (x, y + label_surface.get_height() + 6))

    def _draw_health_bar(self, rect, health, shield_active):
        x = rect.x + 22
        y = rect.y + 18
        bar_width = rect.width - 44
        bar_height = 28
        ratio = max(0, min(1, health / 100))

        label = self.text_font.render("Health", True, MUTED_TEXT_COLOR)
        value = self.text_font.render(f"{health}/100", True, TEXT_COLOR)
        self.surface.blit(label, (x, y))
        value_rect = value.get_rect(topright=(x + bar_width, y))
        self.surface.blit(value, value_rect)

        bar_y = y + label.get_height() + 14
        pygame.draw.rect(
            self.surface,
            HEALTH_BACKGROUND_COLOR,
            (x, bar_y, bar_width, bar_height),
            border_radius=14,
        )
        pygame.draw.rect(
            self.surface,
            HEALTH_SHIELD_FILL_COLOR if shield_active else HEALTH_FILL_COLOR,
            (x, bar_y, round(bar_width * ratio), bar_height),
            border_radius=14,
        )
        pygame.draw.rect(
            self.surface,
            PANEL_BORDER_COLOR,
            (x, bar_y, bar_width, bar_height),
            width=2,
            border_radius=14,
        )

    def _draw_status(self, rect, state):
        dot_color = STATUS_COLORS.get(state.status.value, TEXT_COLOR)
        x = rect.x + 22
        effect_y = rect.y + 136
        effect_width = rect.width - 44
        column_width = (effect_width - EFFECT_COLUMN_GAP) // 2
        left_x = x
        right_x = x + column_width + EFFECT_COLUMN_GAP
        divider_x = left_x + column_width + EFFECT_COLUMN_GAP // 2
        divider_top = effect_y - 2
        effect_rows = (
            ((self._format_status(state), dot_color), (self._format_speed(state), TEXT_COLOR)),
            ((self._format_damage(state), TEXT_COLOR), (self._format_score_effect(state), TEXT_COLOR)),
        )

        for left_cell, right_cell in effect_rows:
            (left_label, left_value), left_color = left_cell
            (right_label, right_value), right_color = right_cell
            self._draw_effect_row(left_x, effect_y, column_width, left_label, left_value, value_color=left_color)
            self._draw_effect_row(right_x, effect_y, column_width, right_label, right_value, value_color=right_color)
            effect_y += self.effect_font.get_height() + EFFECT_ROW_GAP

        divider_bottom = effect_y + self.effect_font.get_height() + 2
        self._draw_effect_row(left_x, effect_y, effect_width, *self._format_special(state))
        pygame.draw.line(self.surface, PANEL_DIVIDER_COLOR, (divider_x, divider_top), (divider_x, divider_bottom), 2)

    def _draw_effect_row(self, x, y, width, label, value, value_color=TEXT_COLOR):
        label_surface = self.effect_font.render(label, True, MUTED_TEXT_COLOR)
        value_surface = self.effect_font.render(value, True, value_color)
        self.surface.blit(label_surface, (x, y))
        value_rect = value_surface.get_rect(topright=(x + width, y))
        min_value_x = x + label_surface.get_width() + EFFECT_LABEL_GAP
        value_rect.x = max(value_rect.x, min_value_x)
        self.surface.blit(value_surface, value_rect)

    def _format_status(self, state):
        label = state.status.value.title()
        if state.status == Status.NORMAL:
            return "Status", label
        return "Status", f"{label} ({state.status_turns})"

    def _format_speed(self, state):
        if state.speed_effect == SpeedEffect.NORMAL:
            return "Speed", "Normal"
        label = "Slower" if state.speed_effect == SpeedEffect.SLOWER else "Faster"
        return "Speed", f"{label} ({state.speed_turns})"

    def _format_damage(self, state):
        if state.damage_effect == DamageEffect.NORMAL:
            return "Damage", "Normal"
        label = "Reduced" if state.damage_effect == DamageEffect.REDUCED else "Increased"
        return "Damage", f"{label} ({state.damage_turns})"

    def _format_score_effect(self, state):
        if state.score_effect == ScoreEffect.NORMAL:
            return "Score", "Normal"
        label = "Boosted" if state.score_effect == ScoreEffect.BOOSTED else "Reduced"
        return "Score", f"{label} ({state.score_turns})"

    def _format_special(self, state):
        if state.special_effect == SpecialEffect.NONE:
            return "Special effect", "None"

        return "Special effect", f"{SPECIAL_LABELS[state.special_effect]} ({state.special_turns})"

    def _draw_score(self, rect, state):
        self._draw_label_value("Score", state.score, rect.x + 22, rect.y + 18)

    def _draw_level(self, rect, level):
        self._draw_label_value("Level", level, rect.x + 22, rect.y + 112, QUESTION_COLOR)

    def _draw_question(self, rect, state, is_question_answered):
        label = self.text_font.render("Question", True, MUTED_TEXT_COLOR)
        color = QUESTION_CORRECT_COLOR if is_question_answered else QUESTION_COLOR
        question = self.question_font.render(state.current_problem.text, True, color)
        self.surface.blit(label, (rect.x, rect.y))
        question_rect = question.get_rect(midleft=(rect.x, rect.y + 78))
        question_rect.left = rect.x
        self.surface.blit(question, question_rect)

    def _draw_input(self, rect, state):
        label = self.text_font.render("Answer", True, MUTED_TEXT_COLOR)
        field_rect = pygame.Rect(rect.x, rect.y + 56, rect.width, 64)
        value = state.answer_text if state.answer_text else "_"
        value_surface = self.text_font.render(value, True, TEXT_COLOR)

        self.surface.blit(label, (rect.x, rect.y))
        pygame.draw.rect(self.surface, INPUT_BACKGROUND_COLOR, field_rect, border_radius=14)
        pygame.draw.rect(self.surface, INPUT_BORDER_COLOR, field_rect, width=2, border_radius=14)
        self.surface.blit(value_surface, (field_rect.x + 18, field_rect.y + 14))
