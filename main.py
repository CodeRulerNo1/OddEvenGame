import pygame
import sys
import random
import time
import math
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Game Constants ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
BUTTON = (100, 100, 100)
DARK_GREY = (64, 64, 64)
BLUE = (70, 130, 180)
ORANGE = (255, 69, 0)

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Odd or Even Hand Cricket")

# Define fonts
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)
font_vsmall = pygame.font.Font(None, 18)

# Define game states
TOSS_STATE = 0
TOSS_PLAY_STATE = 1
CHOOSE_STATE = 2
PLAYING_STATE = 3
RESULT_STATE = 4


class HandCricketGame:

    def __init__(self):
        # Game state variables
        self.current_score = 0
        self.player1_score = 0
        self.player2_score = 0
        self.current_innings = 1  # 1 for Player 1, 2 for Player 2
        self.target = 0

        self.game_over = False
        self.message = "Player, choose Odd or Even to toss."
        self.last_bowler_choice = None
        self.player_hand_image = None
        self.bowler_hand_image = None
        self.lower_hand_image = None
        self.BUTTON_COLOR = (100, 100, 100)
        self.Atext_color = (186, 140, 99)
        self.Otext_color = (255, 114, 118)
        # Toss variables
        self.current_state = TOSS_STATE
        self.toss_choice = None
        self.toss_winner = None
        self.toss_bat_bowl_choice = None
        self.player1_is_batting_first = None

        # Load hand images
        self.hand_images = self.load_hand_images()
        self.load_lower_hand_images()

        # Hexagon center and radius for triangular buttons
        self.hex_center = (SCREEN_WIDTH // 2, 450)
        self.hex_radius = 80

        # Create 6 triangular button areas (as polygons)
        self.triangle_buttons = []
        for i in range(6):
            angle = i * 60 - 90  # Start from top, go clockwise
            # Each triangle: center point, and two edge points
            center_x, center_y = self.hex_center

            # Calculate triangle vertices
            angle_rad = math.radians(angle)
            angle_next_rad = math.radians(angle + 60)

            # Triangle vertices: center + two outer points
            triangle = [
                (center_x, center_y),  # Center point
                (center_x + self.hex_radius * math.cos(angle_rad),
                 center_y + self.hex_radius * math.sin(angle_rad)),
                (center_x + self.hex_radius * math.cos(angle_next_rad),
                 center_y + self.hex_radius * math.sin(angle_next_rad))
            ]
            self.triangle_buttons.append(triangle)

        self.restart_button_rect = pygame.Rect(125, 530, 150, 45)

        # Toss buttons with better positioning
        self.odd_button_rect = pygame.Rect(50, 250, 140, 55)
        self.even_button_rect = pygame.Rect(210, 250, 140, 55)

        # Bat/Bowl choice buttons with better positioning
        self.bat_button_rect = pygame.Rect(50, 250, 140, 55)
        self.bowl_button_rect = pygame.Rect(210, 250, 140, 55)

    def load_lower_hand_images(self):
        image_path = resource_path(f"nimages/hands[-1].png")
        try:
            image_surface = pygame.image.load(image_path)
            # Force scale the image to the new, fixed dimensions
            self.lower_hand_image = pygame.transform.scale(
                image_surface, (200, 50))
        except pygame.error:
            print(
                f"Warning: Could not load image at {image_path}. Using fallback surface."
            )
            # Create a fallback surface with the hand number displayed
            fallback_surface = pygame.Surface((200, 100))
            fallback_surface.fill(GRAY)
            font = pygame.font.Font(None, 48)
            text = font.render("-1", True, BLACK)
            text_rect = text.get_rect(center=(200 / 2, 100 / 2))
            fallback_surface.blit(text, text_rect)
            self.lower_hand_image = fallback_surface

    def load_hand_images(self):
        """Loads hand images from files, forcing a fixed width and height."""
        images = {}
        new_width = 200
        new_height = 100
        for i in range(0, 7):
            image_path = resource_path(f"nimages/hands[{i}].png")
            try:
                image_surface = pygame.image.load(image_path)
                # Force scale the image to the new, fixed dimensions
                images[i] = pygame.transform.scale(image_surface,
                                                   (new_width, new_height))
            except pygame.error:
                print(
                    f"Warning: Could not load image at {image_path}. Using fallback surface."
                )
                # Create a fallback surface with the hand number displayed
                fallback_surface = pygame.Surface((new_width, new_height))
                fallback_surface.fill(GRAY)
                font = pygame.font.Font(None, 48)
                text = font.render(str(i), True, BLACK)
                text_rect = text.get_rect(center=(new_width / 2,
                                                  new_height / 2))
                fallback_surface.blit(text, text_rect)
                images[i] = fallback_surface
        return images

    def draw_text(self, surface, text, font, color, pos):
        """Helper function to render and blit text."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=pos)
        surface.blit(text_surface, text_rect)

    def draw_score_trapeziums(self):
        """Draw trapezium shapes showing each player's score at the top."""
        # Left trapezium for Player 1
        left_trap = [
            (20, 10),  # top-left
            (170, 10),  # top-right
            (150, 40),  # bottom-right
            (40, 40)  # bottom-left
        ]

        # Right trapezium for Player 2/Computer
        right_trap = [
            (230, 10),  # top-left
            (380, 10),  # top-right
            (360, 40),  # bottom-right
            (250, 40)  # bottom-left
        ]

        # Determine colors based on game state
        if self.current_state >= PLAYING_STATE:
            if self.player1_is_batting_first:
                if self.current_innings == 1:
                    left_color = (186, 140, 99)  # Player batting
                    right_color = (255, 114, 118)  # Computer bowling
                else:
                    left_color = (255, 114, 118)  # Player bowling
                    right_color = (186, 140, 99)  # Computer batting
            else:
                if self.current_innings == 1:
                    left_color = (255, 114, 118)  # Player bowling
                    right_color = (186, 140, 99)  # Computer batting
                else:
                    left_color = (186, 140, 99)  # Player batting
                    right_color = (255, 114, 118)  # Computer bowling
        else:
            left_color = BUTTON
            right_color = BUTTON

        # Draw trapeziums
        pygame.draw.polygon(screen, left_color, left_trap)
        pygame.draw.polygon(screen, DARK_GREY, left_trap, 2)  # Border

        pygame.draw.polygon(screen, right_color, right_trap)
        pygame.draw.polygon(screen, DARK_GREY, right_trap, 2)  # Border

        # Draw scores
        player1_display_score = self.player1_score if self.current_state >= RESULT_STATE else (
            self.current_score if
            (self.player1_is_batting_first and self.current_innings == 1) or
            (not self.player1_is_batting_first and self.current_innings == 2)
            else self.player1_score)
        player2_display_score = self.player2_score if self.current_state >= RESULT_STATE else (
            self.current_score if
            (not self.player1_is_batting_first and self.current_innings == 1)
            or (self.player1_is_batting_first and self.current_innings == 2)
            else self.player2_score)

        self.draw_text(screen, "Player", font_vsmall, WHITE, (95, 18))
        self.draw_text(screen, str(player1_display_score), font_small, WHITE,
                       (95, 32))

        self.draw_text(screen, "Computer", font_vsmall, WHITE, (305, 18))
        self.draw_text(screen, str(player2_display_score), font_small, WHITE,
                       (305, 32))

    def point_in_triangle(self, point, triangle):
        """Check if a point is inside a triangle using barycentric coordinates."""
        x, y = point
        x1, y1 = triangle[0]
        x2, y2 = triangle[1]
        x3, y3 = triangle[2]

        # Calculate barycentric coordinates
        denominator = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if abs(denominator) < 1e-10:  # Triangle is degenerate
            return False

        a = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / denominator
        b = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / denominator
        c = 1 - a - b

        return a >= 0 and b >= 0 and c >= 0

    def draw(self):
        """Draw all game elements to the screen."""
        screen.fill(DARK_GREY)

        # Draw trapezium score displays at the top
        self.draw_score_trapeziums()

        # Title with more padding from top
        #self.draw_text(screen, "Hand Cricket", font_large, WHITE, (SCREEN_WIDTH // 2, 70))

        # Innings and Score (only visible in PLAYING state) with better spacing
        #if self.current_state >= PLAYING_STATE:
        #self.draw_text(screen, f"Innings {self.current_innings}", font_medium, WHITE, (SCREEN_WIDTH // 2, 105))
        #self.draw_text(screen, f"Score: {self.current_score}", font_medium, WHITE, (SCREEN_WIDTH // 2, 130))

        # Target display with padding
        #if self.current_innings == 2 and self.target > 0:
        #elf.draw_text(screen, f"Target: {self.target}", font_small, WHITE, (SCREEN_WIDTH // 2, 155))

        # Status message with better positioning and wrapping
        message_y = 195 if self.current_state >= PLAYING_STATE else 135

        # Split long messages into multiple lines for better display
        message_lines = []
        if len(self.message) > 50:
            words = self.message.split(' ')
            current_line = ""
            for word in words:
                if len(current_line + word) < 50:
                    current_line += word + " "
                else:
                    message_lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                message_lines.append(current_line.strip())
        else:
            message_lines = [self.message]

        for i, line in enumerate(message_lines):
            self.draw_text(screen, line, font_small, WHITE,
                           (SCREEN_WIDTH // 2, message_y + i * 20))

        if self.current_state == TOSS_STATE:
            # Draw toss buttons with more padding
            pygame.draw.rect(screen,
                             ORANGE,
                             self.odd_button_rect,
                             border_radius=8)
            self.draw_text(screen, "Odd", font_medium, WHITE,
                           self.odd_button_rect.center)
            pygame.draw.rect(screen,
                             BLUE,
                             self.even_button_rect,
                             border_radius=8)
            self.draw_text(screen, "Even", font_medium, WHITE,
                           self.even_button_rect.center)

        elif self.current_state == CHOOSE_STATE:
            # Draw bat/bowl buttons with more padding
            pygame.draw.rect(screen,
                             self.Atext_color,
                             self.bat_button_rect,
                             border_radius=8)
            self.draw_text(screen, "Bat", font_medium, WHITE,
                           self.bat_button_rect.center)
            pygame.draw.rect(screen,
                             self.Otext_color,
                             self.bowl_button_rect,
                             border_radius=8)
            self.draw_text(screen, "Bowl", font_medium, WHITE,
                           self.bowl_button_rect.center)

        elif self.current_state >= TOSS_PLAY_STATE:
            # Display hand images with better spacing
            hand_y_position = 250

            # Show player hand image (default to hands[0] if no selection made)
            player_image = self.player_hand_image if self.player_hand_image else self.hand_images[
                0]
            screen.blit(player_image, (-25, hand_y_position))
            self.draw_text(screen, "Batsman", font_small, self.Atext_color,
                           (player_image.get_width() // 2,
                            hand_y_position + player_image.get_height() - 120))
            if self.lower_hand_image:
                screen.blit(self.lower_hand_image,
                            (-25, hand_y_position + 100))

            # Show bowler hand image (default to hands[0] if no selection made)
            bowler_image = self.bowler_hand_image if self.bowler_hand_image else self.hand_images[
                0]
            flipped_image = pygame.transform.flip(bowler_image, True, False)
            screen.blit(flipped_image,
                        (SCREEN_WIDTH - flipped_image.get_width() + 25,
                         hand_y_position))
            self.draw_text(
                screen, "Bowler", font_small, self.Otext_color,
                (SCREEN_WIDTH - flipped_image.get_width() // 2,
                 hand_y_position + flipped_image.get_height() - 120))
            if self.lower_hand_image:
                flipped_lower_image = pygame.transform.flip(
                    self.lower_hand_image, True, False)
                screen.blit(flipped_lower_image,
                            (SCREEN_WIDTH - flipped_lower_image.get_width() +
                             25, hand_y_position + 100))
            # Draw hexagonal triangular buttons
            for i, triangle in enumerate(self.triangle_buttons):
                # Draw triangle button
                pygame.draw.polygon(screen, self.BUTTON_COLOR, triangle)
                pygame.draw.polygon(screen, BLACK, triangle, 3)  # Border

                # Calculate text position (centroid of triangle)
                text_x = sum(point[0] for point in triangle) // 3
                text_y = sum(point[1] for point in triangle) // 3

                self.draw_text(screen, str(i + 1), font_medium, WHITE,
                               (text_x, text_y))

        # Restart button with padding from bottom
        pygame.draw.rect(screen,
                         GREEN,
                         self.restart_button_rect,
                         border_radius=8)
        self.draw_text(screen, "Restart", font_small, WHITE,
                       self.restart_button_rect.center)

        pygame.display.flip()

    def handle_click(self, pos):
        """Processes clicks on buttons based on the current state."""
        if self.restart_button_rect.collidepoint(pos):
            self.restart_game()
            return

        if self.current_state == TOSS_STATE:
            self.Otext_color = (100, 100, 100)
            self.Atext_color = (100, 100, 100)
            if self.odd_button_rect.collidepoint(pos):
                self.toss_choice = "Odd"
                self.message = "Now choose a number for the toss."
                self.current_state = TOSS_PLAY_STATE
            elif self.even_button_rect.collidepoint(pos):
                self.toss_choice = "Even"
                self.message = "Now choose a number for the toss."
                self.current_state = TOSS_PLAY_STATE

        elif self.current_state == TOSS_PLAY_STATE:
            for i, triangle in enumerate(self.triangle_buttons):
                if self.point_in_triangle(pos, triangle):
                    self.play_toss_turn(i + 1)
                    break

        elif self.current_state == CHOOSE_STATE:
            if self.bat_button_rect.collidepoint(pos):
                self.toss_bat_bowl_choice = "Bat"
                self.set_first_innings()
            elif self.bowl_button_rect.collidepoint(pos):
                self.toss_bat_bowl_choice = "Bowl"
                self.set_first_innings()

        elif self.current_state == PLAYING_STATE:
            for i, triangle in enumerate(self.triangle_buttons):
                if self.point_in_triangle(pos, triangle):
                    self.play_turn(i + 1)
                    break

        elif self.current_state == RESULT_STATE:
            # No action, wait for restart
            pass

    def play_toss_turn(self, player_choice):
        """Logic for the odd/even toss after the initial choice."""
        bowler_choice = random.randint(1, 6)
        self.BUTTON_COLOR = (100, 100, 100)
        self.Atext_color = (100, 100, 100)
        self.Otext_color = (100, 100, 100)
        self.player_hand_image = self.hand_images.get(player_choice)
        self.bowler_hand_image = self.hand_images.get(bowler_choice)

        total = player_choice + bowler_choice
        result = "Even" if total % 2 == 0 else "Odd"

        self.message = f"You: {player_choice}, Computer: {bowler_choice}. Total: {total} ({result})."

        self.draw()
        time.sleep(2)

        if self.toss_choice == result:
            self.toss_winner = "Player"
            self.message = "Player wins the toss! Choose to Bat or Bowl."
            self.current_state = CHOOSE_STATE
        else:
            self.toss_winner = "Computer"
            self.message = "Computer wins the toss and chooses to Bat."
            self.toss_bat_bowl_choice = "Bat"
            self.set_first_innings()
        self.player_hand_image = None
        self.bowler_hand_image = None
        self.draw()
        time.sleep(1)
        self.Atext_color = (186, 140, 99)
        self.Otext_color = (255, 114, 118)

    def set_first_innings(self):
        """Sets up the game based on the toss winner's choice."""
        if self.toss_winner == "Player":
            if self.toss_bat_bowl_choice == "Bat":
                self.BUTTON_COLOR = (186, 140, 99)
                self.player1_is_batting_first = True
                self.message = "Player is batting first."
            else:
                self.BUTTON_COLOR = (255, 114, 118)
                self.player1_is_batting_first = False
                self.message = "Player is bowling first."
        else:  # Computer won toss and its choice is already determined as "Bat"
            computer_choice = random.choice(["Bat", "Bowl"])
            if computer_choice == 'Bat':
                self.BUTTON_COLOR = (255, 114, 118)
                self.player1_is_batting_first = False
                self.message = "Computer is batting first."
            else:
                self.BUTTON_COLOR = (186, 140, 99)
                self.player1_is_batting_first = True
                self.message = "Computer is bowling first."

        self.current_state = PLAYING_STATE
        self.current_innings = 1

        if not self.player1_is_batting_first:
            # If computer is batting first, simulate its innings
            self.message = "Computer's turn to bat. Please select a number to bowl."

    def play_turn(self, player_choice):
        """Main game logic for a single turn."""
        # Determine who is batting and who is bowling
        player_is_batting = (self.player1_is_batting_first and self.current_innings == 1) or \
                            (not self.player1_is_batting_first and self.current_innings == 2)

        if player_is_batting:

            self.player_hand_image = self.hand_images.get(player_choice)

            bowler_choice = random.randint(1, 6)
            self.bowler_hand_image = self.hand_images.get(bowler_choice)

            if player_choice == bowler_choice:
                self.message = f"Computer chose {bowler_choice}. OUT! Final score: {self.current_score}"
                self.end_innings()
            else:
                self.current_score += player_choice
                self.message = f"Computer chose {bowler_choice}. Scored {player_choice} runs."
                # Check if target is reached in second innings
                if self.current_innings == 2 and self.current_score >= self.target:
                    self.message += f"\nTarget reached! Game won!"
                    self.end_innings()
        else:
            # Player is bowling

            player_hand = random.randint(1, 6)
            self.player_hand_image = self.hand_images.get(player_hand)
            self.bowler_hand_image = self.hand_images.get(player_choice)

            if player_hand == player_choice:
                self.message = f"You chose {player_choice}. OUT! Final score: {self.current_score}"
                self.end_innings()
            else:
                self.current_score += player_hand
                self.message = f"You chose {player_choice}. Computer scored {player_hand} runs."
                # Check if target is reached in second innings
                if self.current_innings == 2 and self.current_score >= self.target:
                    self.message += f"\nTarget reached! Game won!"
                    self.end_innings()

    def end_innings(self):
        """Ends the current innings and transitions to the next."""
        if self.current_innings == 1:
            if self.player1_is_batting_first:
                self.player1_score = self.current_score
                self.target = self.player1_score + 1
            else:
                self.player2_score = self.current_score
                self.target = self.player2_score + 1

            self.message += f"\nTarget to chase: {self.target} runs."
            self.draw()
            time.sleep(2)

            self.current_innings = 2
            self.current_score = 0
            self.player_hand_image = None
            self.bowler_hand_image = None
            if self.player1_is_batting_first:
                self.message = "Computer is batting. Please select a number to bowl."
                self.BUTTON_COLOR = (255, 114, 118)
            else:
                self.message = "Player, it's your turn to bat!"
                self.BUTTON_COLOR = (186, 140, 99)

        elif self.current_innings == 2:
            if self.player1_is_batting_first:
                self.BUTTON_COLOR = (255, 114, 118)
                self.player2_score = self.current_score
            else:
                self.BUTTON_COLOR = (186, 140, 99)
                self.player1_score = self.current_score
            self.show_result()

    def show_result(self):
        """Determines and displays the final game result."""
        self.current_state = RESULT_STATE
        self.game_over = True

        if self.player1_is_batting_first:
            self.BUTTON_COLOR = (100, 100, 100)
            if self.player2_score >= self.target:
                self.message = f"Computer wins! Score: {self.player2_score}"
            elif self.player1_score > self.player2_score:
                self.message = f"Player wins! Score: {self.player1_score}"
            else:
                self.message = f"It's a Tie! Both scored {self.player1_score}"
        else:
            self.BUTTON_COLOR = (100, 100, 100)
            if self.player1_score >= self.target:
                self.message = f"Player wins! Score: {self.player1_score}"
            elif self.player2_score > self.player1_score:
                self.message = f"Computer wins! Score: {self.player2_score}"
            else:
                self.message = f"It's a Tie! Both scored {self.player1_score}"

    def restart_game(self):
        """Resets all game state variables."""
        self.current_score = 0
        self.player1_score = 0
        self.player2_score = 0
        self.current_innings = 1
        self.target = 0
        self.game_over = False
        self.player_hand_image = None
        self.bowler_hand_image = None
        self.last_bowler_choice = None
        self.current_state = TOSS_STATE
        self.toss_choice = None
        self.toss_winner = None
        self.toss_bat_bowl_choice = None
        self.player1_is_batting_first = None
        self.message = "Player , choose Odd or Even to toss."
        self.BUTTON_COLOR = (100, 100, 100)
        self.Atext_color = (100, 100, 100)
        self.Otext_color = (100, 100, 100)


# --- Main Game Loop ---
def main():
    game = HandCricketGame()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)

        game.draw()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
