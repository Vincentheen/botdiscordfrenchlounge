import discord
from discord import errors as discord_errors
import sys

# Classe pour le bouton d'attribution du rôle giveaway
class GiveawayRoleView(discord.ui.View):
    def __init__(self, participant_role_id, winner_role_id, giveaway_id=None):
        super().__init__(timeout=None)  # Pas de timeout pour que le bouton reste actif
        self.participant_role_id = participant_role_id
        self.winner_role_id = winner_role_id
        self.giveaway_id = giveaway_id  # ID du message de giveaway pour accéder au dictionnaire giveaways

    @discord.ui.button(label="🎁 Participer au giveaway",
                      style=discord.ButtonStyle.success,
                      custom_id="giveaway_role_button")
    async def giveaway_role_button(self, button, interaction):
        print(f"=== Bouton de participation au giveaway cliqué ===")

        # Déterminer quel paramètre est l'interaction
        if isinstance(button, discord.Interaction):
            real_interaction = button
        elif isinstance(interaction, discord.Interaction):
            real_interaction = interaction
        else:
            print(f"Aucun paramètre n'est une interaction valide")
            return

        print(f"Utilisateur: {real_interaction.user.name} (ID: {real_interaction.user.id})")

        try:
            # Vérifier si l'utilisateur a déjà le rôle de gagnant
            winner_role = discord.utils.get(real_interaction.guild.roles, id=self.winner_role_id)
            if winner_role and winner_role in real_interaction.user.roles:
                try:
                    await real_interaction.response.send_message(
                        "❌ Tu as déjà gagné un giveaway précédent. Tu ne peux pas participer à ce giveaway.",
                        ephemeral=True
                    )
                except discord_errors.InteractionResponded:
                    try:
                        await real_interaction.followup.send(
                            "❌ Tu as déjà gagné un giveaway précédent. Tu ne peux pas participer à ce giveaway.",
                            ephemeral=True
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'envoi du message de suivi: {e}")
                return

            # Rechercher le rôle de participant au giveaway
            print(f"Recherche du rôle de participant (ID: {self.participant_role_id}) dans le serveur {real_interaction.guild.name}")
            participant_role = discord.utils.get(real_interaction.guild.roles, id=self.participant_role_id)

            if not participant_role:
                print(f"❌ Rôle de participant introuvable dans le serveur {real_interaction.guild.name}")
                # Afficher tous les rôles disponibles pour le débogage
                available_roles = [f"{r.name} (ID: {r.id})" for r in real_interaction.guild.roles]
                print(f"Rôles disponibles: {', '.join(available_roles)}")

                try:
                    await real_interaction.response.send_message(
                        "❌ Le rôle de participant est introuvable. Contacte un administrateur.",
                        ephemeral=True
                    )
                except discord_errors.InteractionResponded:
                    try:
                        await real_interaction.followup.send(
                            "❌ Le rôle de participant est introuvable. Contacte un administrateur.",
                            ephemeral=True
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'envoi du message de suivi: {e}")
                return

            print(f"✅ Rôle de participant trouvé: {participant_role.name} (ID: {participant_role.id})")

            # Vérifier si l'utilisateur a déjà le rôle de participant
            if participant_role in real_interaction.user.roles:
                # L'utilisateur a déjà le rôle, mais assurons-nous qu'il est dans la liste des participants
                message_id = real_interaction.message.id
                
                # Ajouter l'utilisateur à la liste des participants du giveaway
                try:
                    # Obtenir le module main
                    main_module = None
                    for module_name, module in sys.modules.items():
                        if hasattr(module, 'giveaways') and module_name != 'giveaway_role_view':
                            main_module = module
                            break
                    
                    if main_module and hasattr(main_module, 'giveaways'):
                        giveaways = main_module.giveaways
                        
                        # Vérifier si le giveaway existe
                        if message_id in giveaways:
                            # Ajouter l'utilisateur à la liste des participants
                            giveaways[message_id]["participants"].add(real_interaction.user)
                            print(f"Utilisateur {real_interaction.user.name} ajouté aux participants du giveaway {message_id}")
                except Exception as e:
                    print(f"Erreur lors de l'ajout de l'utilisateur aux participants: {e}")
                
                try:
                    await real_interaction.response.send_message(
                        "✅ Tu participes déjà à ce giveaway !",
                        ephemeral=True
                    )
                except discord_errors.InteractionResponded:
                    try:
                        await real_interaction.followup.send(
                            "✅ Tu participes déjà à ce giveaway !",
                            ephemeral=True
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'envoi du message de suivi: {e}")
                return

            # Vérifier la hiérarchie des rôles
            bot_member = real_interaction.guild.get_member(real_interaction.client.user.id)
            if bot_member.top_role.position <= participant_role.position:
                try:
                    await real_interaction.response.send_message(
                        "❌ Je n'ai pas la permission d'attribuer ce rôle. Contacte un administrateur.",
                        ephemeral=True
                    )
                except discord_errors.InteractionResponded:
                    try:
                        await real_interaction.followup.send(
                            "❌ Je n'ai pas la permission d'attribuer ce rôle. Contacte un administrateur.",
                            ephemeral=True
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'envoi du message de suivi: {e}")
                return

            # Attribuer le rôle de participant
            await real_interaction.user.add_roles(participant_role)
            print(f"Rôle de participant {participant_role.name} ajouté à {real_interaction.user.name}")

            # Ajouter l'utilisateur à la liste des participants du giveaway
            message_id = real_interaction.message.id
            
            # Essayer d'accéder au dictionnaire giveaways du module principal
            try:
                # Obtenir le module main
                main_module = None
                for module_name, module in sys.modules.items():
                    if hasattr(module, 'giveaways') and module_name != 'giveaway_role_view':
                        main_module = module
                        break
                
                if main_module and hasattr(main_module, 'giveaways'):
                    giveaways = main_module.giveaways
                    
                    # Vérifier si le giveaway existe
                    if message_id in giveaways:
                        # Ajouter l'utilisateur à la liste des participants
                        giveaways[message_id]["participants"].add(real_interaction.user)
                        print(f"Utilisateur {real_interaction.user.name} ajouté aux participants du giveaway {message_id}")
                    else:
                        print(f"Giveaway {message_id} non trouvé dans le dictionnaire giveaways")
            except Exception as e:
                print(f"Erreur lors de l'ajout de l'utilisateur aux participants: {e}")

            # Confirmer à l'utilisateur
            try:
                await real_interaction.response.send_message(
                    f"✅ Tu participes maintenant au giveaway ! Bonne chance !",
                    ephemeral=True
                )
            except discord_errors.InteractionResponded:
                try:
                    await real_interaction.followup.send(
                        f"✅ Tu participes maintenant au giveaway ! Bonne chance !",
                        ephemeral=True
                    )
                except Exception as e:
                    print(f"Erreur lors de l'envoi du message de confirmation: {e}")

        except discord.Forbidden:
            try:
                await real_interaction.response.send_message(
                    "❌ Je n'ai pas la permission d'attribuer ce rôle. Contacte un administrateur.",
                    ephemeral=True
                )
            except discord_errors.InteractionResponded:
                # L'interaction a déjà reçu une réponse
                try:
                    await real_interaction.followup.send(
                        "❌ Je n'ai pas la permission d'attribuer ce rôle. Contacte un administrateur.",
                        ephemeral=True
                    )
                except Exception as e2:
                    print(f"Erreur lors de l'envoi du message de suivi: {e2}")
        except Exception as e:
            print(f"Erreur lors de l'attribution du rôle de participant: {e}")
            try:
                await real_interaction.response.send_message(
                    "❌ Une erreur s'est produite. Contacte un administrateur.",
                    ephemeral=True
                )
            except discord_errors.InteractionResponded:
                # L'interaction a déjà reçu une réponse
                try:
                    await real_interaction.followup.send(
                        "❌ Une erreur s'est produite. Contacte un administrateur.",
                        ephemeral=True
                    )
                except Exception as e2:
                    print(f"Erreur lors de l'envoi du message de suivi: {e2}")
