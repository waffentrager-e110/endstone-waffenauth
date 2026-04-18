from endstone.form import ModalForm, CustomForm
from endstone import Server
import logging

def show_login_form(player, auth_instance):
    """Show the login form to the player."""
    form = CustomForm()
    form.title("Login")
    form.input("Username", placeholder="Enter your username...")
    form.password("Password", placeholder="Enter your password...")

    def handle_response(player, response):
        if response is None:
            # Player closed the form, kick them
            player.kick("You must complete the authentication process.")
            return

        username_input, password_input = response
        if not username_input or not password_input:
            player.send_message("§cPlease fill in both fields.")
            show_login_form(player, auth_instance)
            return

        # Validate credentials
        if auth_instance.database.user_exists(username_input) and auth_instance.database.verify_password(username_input, password_input):
            # Success
            auth_instance.database.clear_failed_attempts(player.name)
            auth_instance.server.add_player_permission(player, "wt.login")
            player.send_message("§aLogin successful! Welcome back.")
            logging.info(f"[WaffenAuth] Player {player.name} logged in successfully.")
        else:
            # Failure
            auth_instance.database.log_failed_attempt(player.name)
            attempts = auth_instance.database.get_failed_attempts_count(player.name)
            max_attempts = auth_instance.max_attempts # Access from main plugin instance

            if attempts >= max_attempts:
                player.kick(f"Too many failed login attempts ({attempts}). Try again later.")
                logging.warning(f"[WaffenAuth] Player {player.name} kicked due to too many failed attempts.")
            else:
                remaining = max_attempts - attempts
                player.send_message(f"§cInvalid credentials. Attempts left: {remaining}.")
                show_login_form(player, auth_instance) # Show form again

    form.set_response_callback(handle_response)
    player.show_form(form)


def show_register_form(player, auth_instance):
    """Show the registration form to the player."""
    form = CustomForm()
    form.title("Register")
    form.input("Username", placeholder="Choose a username...")
    form.password("Password", placeholder="Choose a password...")

    def handle_response(player, response):
        if response is None:
            # Player closed the form, kick them
            player.kick("You must complete the authentication process.")
            return

        username_input, password_input = response
        if not username_input or not password_input:
            player.send_message("§cPlease fill in both fields.")
            show_register_form(player, auth_instance)
            return

        # Check if username already exists
        if auth_instance.database.user_exists(username_input):
            player.send_message("§cUsername already taken. Please choose another one.")
            show_register_form(player, auth_instance)
            return

        # Register new user
        if auth_instance.database.add_user(username_input, password_input):
            auth_instance.server.add_player_permission(player, "wt.login")
            player.send_message("§aRegistration successful! Welcome.")
            logging.info(f"[WaffenAuth] Player {player.name} registered as {username_input}.")
        else:
            # This case handles potential DB errors during insertion
            player.send_message("§cRegistration failed due to a server error. Please try again.")
            logging.error(f"[WaffenAuth] Failed to register user {username_input} for player {player.name}.")

    form.set_response_callback(handle_response)
    player.show_form(form)
