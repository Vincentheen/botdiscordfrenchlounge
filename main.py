import discord
from discord.ext import commands
import random
import asyncio
import os
import datetime
from keep_alive import keep_alive
import json

# Configuration des intents (une seule fois)
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

#IDs des canaux et rôles
LOG_CHANNEL_ID = 1357111972486840472
LOG_TICKET_ID = 1357112024483631246
LOG_FLUX_ID = 1357125840982249644
LOG_JOIN_LEAVE_ID = 1357111972486840472  # ID du canal pour les logs d'arrivées/départs
MUTE_ROLE_ID = 1357046834048139457

# IDs des rôles de staff
OWNER_ROLE_ID = 1354892680735227911    # Propriétaire du serveur
ADMIN_ROLE_ID = 1354900754275504310    # Administrateur (même ID que OWNER pour l'instant)
MOD_ROLE_ID = 1354900001565966337      # Modérateur
HELPER_ROLE_ID = 1354899626997579807   # Helper

# Dictionnaire pour stocker les rôles personnalisés
CUSTOM_ROLES = {}  # Format: {"nom_du_role": {"id": role_id, "permissions": [liste_des_commandes]}}

ROLE_JOIN_ID = 1357113117561192478
GIVEAWAY_WINNER_ROLE_ID = 1357113189762076692
AUTO_ROLE_ID = 1354904148570542273
WELCOME_CHANNEL_ID = 1357046834874421496
GUILD_ID = 1354892680722911405 # ID du serveur


# Fichiers de configuration
CONFIG_FILE = 'config.json'
PERMISSIONS_FILE = 'permissions.json'

# Fonction pour sauvegarder la configuration
def save_config():
    config = {
        'LOG_JOIN_LEAVE_ID': LOG_JOIN_LEAVE_ID,
        'OWNER_ROLE_ID': OWNER_ROLE_ID,
        'ADMIN_ROLE_ID': ADMIN_ROLE_ID,
        'MOD_ROLE_ID': MOD_ROLE_ID,
        'HELPER_ROLE_ID': HELPER_ROLE_ID,
        'CUSTOM_ROLES': CUSTOM_ROLES
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la configuration: {e}")
        return False

# Fonction pour charger la configuration
def load_config():
    global LOG_JOIN_LEAVE_ID, OWNER_ROLE_ID, ADMIN_ROLE_ID, MOD_ROLE_ID, HELPER_ROLE_ID, CUSTOM_ROLES
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            LOG_JOIN_LEAVE_ID = config.get('LOG_JOIN_LEAVE_ID', LOG_JOIN_LEAVE_ID)
            OWNER_ROLE_ID = config.get('OWNER_ROLE_ID', OWNER_ROLE_ID)
            ADMIN_ROLE_ID = config.get('ADMIN_ROLE_ID', ADMIN_ROLE_ID)
            MOD_ROLE_ID = config.get('MOD_ROLE_ID', MOD_ROLE_ID)
            HELPER_ROLE_ID = config.get('HELPER_ROLE_ID', HELPER_ROLE_ID)
            CUSTOM_ROLES = config.get('CUSTOM_ROLES', {})
        return True
    except FileNotFoundError:
        print("Fichier de configuration non trouvé, utilisation des valeurs par défaut")
        return False
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        return False

# Fonction pour sauvegarder les permissions des rôles
def save_permissions():
    try:
        with open(PERMISSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(role_permissions, f, ensure_ascii=False, indent=4)
        print("Permissions des rôles sauvegardées avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des permissions des rôles: {e}")
        return False

# Fonction pour charger les permissions des rôles
def load_permissions():
    global role_permissions
    try:
        with open(PERMISSIONS_FILE, 'r', encoding='utf-8') as f:
            loaded_permissions = json.load(f)

            # Vérifier que les clés de base existent
            if "mod" not in loaded_permissions:
                loaded_permissions["mod"] = role_permissions["mod"]
                print("Clé 'mod' ajoutée aux permissions avec les valeurs par défaut")

            if "helper" not in loaded_permissions:
                loaded_permissions["helper"] = role_permissions["helper"]
                print("Clé 'helper' ajoutée aux permissions avec les valeurs par défaut")

            # S'assurer que chaque rôle a les champs nécessaires
            for role_key in ["mod", "helper"]:
                if "commands" not in loaded_permissions[role_key]:
                    loaded_permissions[role_key]["commands"] = role_permissions[role_key]["commands"]
                    print(f"Champ 'commands' ajouté au rôle {role_key} avec les valeurs par défaut")

                if "description" not in loaded_permissions[role_key]:
                    loaded_permissions[role_key]["description"] = role_permissions[role_key]["description"]
                    print(f"Champ 'description' ajouté au rôle {role_key} avec les valeurs par défaut")

            role_permissions = loaded_permissions
        print("Permissions des rôles chargées avec succès")
        return True
    except FileNotFoundError:
        print("Fichier de permissions non trouvé, utilisation des valeurs par défaut")
        save_permissions()  # Créer le fichier avec les valeurs par défaut
        return False
    except Exception as e:
        print(f"Erreur lors du chargement des permissions des rôles: {e}")
        return False

# Charger la configuration au démarrage
load_config()
load_permissions()



# L'événement on_member_join sera défini après la création de l'instance bot





# Liste des mots interdits
MOTS_INTERDITS = [
    "fdp", "tg","pute","enculé"
]

# Dictionnaire global pour les avertissements (un seul système)
warnings = {}

# Dictionnaire pour suivre les giveaways actifs
giveaways = {}

# Dictionnaire pour stocker les règlements
reglement = {
    "channel_id": None,  # ID du canal où afficher le règlement
    "message_id": None,  # ID du message de règlement
    "rules": [],         # Liste des règles
    "banner_url": "hhttps://media.discordapp.net/attachments/1356391472869544138/1357094017006960790/glace.webp?ex=67eef3cb&is=67eda24b&hm=07365bbd9febea82e5cde3c098ce5c26f7f4b19830d18a91844a8476edfdbb14&=&format=webp&width=701&height=701"  # URL de la bannière du règlement
}

# Dictionnaire pour stocker les permissions des rôles
role_permissions = {
    "mod": {
        "commands": [
            "kick", "mute", "unmute", "warn", "clearwarns", "clear",
            "addrole", "removerole", "addword", "removeword", "listwords",
            "renameticket", "addmember", "removemember", "listtickets"
        ],
        "description": "Modérateurs du serveur"
    },
    "helper": {
        "commands": [
            "warn", "mute", "unmute", "clear", "listwords",
            "renameticket", "addmember", "removemember", "listtickets"
        ],
        "description": "Assistants de modération"
    }
}

# Fonction pour sauvegarder le règlement dans un fichier JSON
def save_reglement():
    try:
        with open('reglement.json', 'w', encoding='utf-8') as f:
            json.dump(reglement, f, ensure_ascii=False, indent=4)
        print("Règlement sauvegardé avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du règlement: {e}")
        return False

# Fonction pour charger le règlement depuis un fichier JSON
def load_reglement():
    global reglement
    try:
        with open('reglement.json', 'r', encoding='utf-8') as f:
            loaded_reglement = json.load(f)

            # S'assurer que toutes les clés nécessaires existent
            default_reglement = {
                "channel_id": None,
                "message_id": None,
                "rules": [],
                "banner_url": "https://i.imgur.com/tJtAdNs.png"
            }

            # Ajouter les clés manquantes du dictionnaire par défaut
            for key, value in default_reglement.items():
                if key not in loaded_reglement:
                    loaded_reglement[key] = value
                    print(f"Clé '{key}' ajoutée au règlement avec la valeur par défaut")

            reglement = loaded_reglement
        print("Règlement chargé avec succès")
        return True
    except FileNotFoundError:
        print("Fichier de règlement non trouvé, utilisation des valeurs par défaut")
        return False
    except Exception as e:
        print(f"Erreur lors du chargement du règlement: {e}")
        return False

class PersistentViewBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.persistent_views_added = False

bot = PersistentViewBot(command_prefix="!", intents=intents, case_insensitive=True)
tickets = {}

# Cette fonction a été fusionnée avec l'autre définition de on_member_join plus bas dans le code
# Voir lignes ~860

# Fonction pour vérifier si un utilisateur a la permission d'utiliser une commande
def has_permission(member, command_name, target_member=None):
    """
    Vérifie si un utilisateur a la permission d'utiliser une commande.

    Args:
        member: Le membre qui exécute la commande
        command_name: Le nom de la commande à vérifier
        target_member: Le membre ciblé par la commande (pour les commandes de modération)

    Returns:
        bool: True si l'utilisateur a la permission, False sinon
    """
    # Vérifier la hiérarchie si une cible est spécifiée
    if target_member:
        # Vérifier si la cible est propriétaire du serveur
        owner_role = discord.utils.get(target_member.guild.roles, id=OWNER_ROLE_ID)
        if owner_role and owner_role in target_member.roles:
            # Seul le propriétaire du serveur peut agir sur un autre propriétaire
            return discord.utils.get(member.guild.roles, id=OWNER_ROLE_ID) in member.roles

        # Vérifier si la cible est administrateur
        admin_role = discord.utils.get(target_member.guild.roles, id=ADMIN_ROLE_ID)
        if admin_role and admin_role in target_member.roles:
            # Seul un propriétaire ou un administrateur peut agir sur un administrateur
            return (discord.utils.get(member.guild.roles, id=OWNER_ROLE_ID) in member.roles or
                    discord.utils.get(member.guild.roles, id=ADMIN_ROLE_ID) in member.roles)

        # Vérifier si la cible est modérateur
        mod_role = discord.utils.get(target_member.guild.roles, id=MOD_ROLE_ID)
        if mod_role and mod_role in target_member.roles:
            # Seul un propriétaire, un administrateur ou un modérateur peut agir sur un modérateur
            return (discord.utils.get(member.guild.roles, id=OWNER_ROLE_ID) in member.roles or
                    discord.utils.get(member.guild.roles, id=ADMIN_ROLE_ID) in member.roles or
                    discord.utils.get(member.guild.roles, id=MOD_ROLE_ID) in member.roles)

    # Vérifier les permissions de l'utilisateur qui exécute la commande

    # Le propriétaire du serveur a toutes les permissions
    if discord.utils.get(member.guild.roles, id=OWNER_ROLE_ID) in member.roles:
        return True

    # Les administrateurs ont toutes les permissions
    if discord.utils.get(member.guild.roles, id=ADMIN_ROLE_ID) in member.roles:
        return True

    # Vérifier si l'utilisateur a le rôle de modérateur
    mod_role = discord.utils.get(member.guild.roles, id=MOD_ROLE_ID)
    if mod_role and mod_role in member.roles:
        return command_name in role_permissions["mod"]["commands"]

    # Vérifier si l'utilisateur a le rôle de helper
    helper_role = discord.utils.get(member.guild.roles, id=HELPER_ROLE_ID)
    if helper_role and helper_role in member.roles:
        return command_name in role_permissions["helper"]["commands"]

    # Vérifier les rôles personnalisés
    for role_name, role_data in CUSTOM_ROLES.items():
        role_id = role_data.get("id")
        role = discord.utils.get(member.guild.roles, id=role_id)
        if role and role in member.roles:
            return command_name in role_data.get("permissions", [])

    # Par défaut, l'utilisateur n'a pas la permission
    return False

# Fonction pour journaliser les actions
async def log_action(ctx, action, member, role=None, reason=None):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        if role:
            await log_channel.send(f'**{action}** : {ctx.author.mention} a {action} le rôle {role.name} à {member.mention}.')
        elif reason:
            await log_channel.send(f'**{action}** : {member.mention} ({member.id})\n📌 Raison : {reason}')
        else:
            await log_channel.send(f'**{action}** : {member.mention} ({member.id})')

# Classes pour les vues des tickets
class CloseTicketView(discord.ui.View):
    def __init__(self, creator_id=None):
        super().__init__(timeout=None)
        self.creator_id = creator_id

    @discord.ui.button(label="Fermer le ticket",
                      style=discord.ButtonStyle.danger,
                      custom_id="close_ticket_button")
    async def close_button(self, button, interaction):
        print(f"=== Bouton fermeture cliqué ===")
        print(f"Type du premier paramètre: {type(button)}")
        print(f"Type du deuxième paramètre: {type(interaction)}")

        # Déterminer quel paramètre est l'interaction
        if isinstance(button, discord.Interaction):
            real_interaction = button
            print(f"L'interaction est le premier paramètre")
        elif isinstance(interaction, discord.Interaction):
            real_interaction = interaction
            print(f"L'interaction est le deuxième paramètre")
        else:
            print(f"Aucun paramètre n'est une interaction valide")
            return

        print(f"Utilisateur: {real_interaction.user.name if hasattr(real_interaction, 'user') and real_interaction.user else 'Non disponible'}")

        try:
            # Vérifier si l'interaction a déjà été répondue
            if real_interaction.response.is_done():
                print("L'interaction a déjà reçu une réponse")
                return

            # Vérifier si les attributs nécessaires sont présents
            if not hasattr(real_interaction, 'user') or not hasattr(real_interaction, 'channel') or not hasattr(real_interaction, 'guild'):
                print(f"Erreur: L'objet interaction n'a pas les attributs nécessaires dans close_button")
                return

            # Vérifier si l'utilisateur a le droit de fermer le ticket
            channel_id = real_interaction.channel.id
            print(f"Canal: {real_interaction.channel.name} (ID: {channel_id})")

            # Si le ticket est dans notre dictionnaire, vérifier le créateur
            if channel_id in tickets:
                creator_id = tickets[channel_id]["creator_id"]
                print(f"Créateur du ticket: {tickets[channel_id]['creator_name']} (ID: {creator_id})")
                if real_interaction.user.id != creator_id and not real_interaction.user.guild_permissions.administrator:
                    print(f"Utilisateur non autorisé à fermer le ticket")
                    await real_interaction.response.send_message(
                        "❌ Tu n'es pas autorisé à fermer ce ticket.",
                        ephemeral=True)
                    return
            # Sinon, utiliser le creator_id de la classe ou vérifier les permissions d'admin
            elif self.creator_id is not None and real_interaction.user.id != self.creator_id and not real_interaction.user.guild_permissions.administrator:
                print(f"Utilisateur non autorisé à fermer le ticket (via creator_id de la classe)")
                await real_interaction.response.send_message(
                    "❌ Tu n'es pas autorisé à fermer ce ticket.",
                    ephemeral=True)
                return

            # Informer que le ticket va être fermé
            print(f"Envoi du message de fermeture...")
            await real_interaction.response.send_message(
                "🔒 Fermeture du ticket en cours...",
                ephemeral=True)

            # Supprimer le ticket du dictionnaire
            if channel_id in tickets:
                print(f"Suppression du ticket du dictionnaire")
                del tickets[channel_id]

            # Log de l'action
            print(f"Recherche du canal de logs...")
            log_channel = discord.utils.get(real_interaction.guild.text_channels, id=LOG_TICKET_ID)
            if log_channel:
                print(f"Envoi du message de log...")
                await log_channel.send(
                    f"🔒 **Fermeture de ticket**\n**Utilisateur** : {real_interaction.user.mention} ({real_interaction.user.id})\n**Ticket fermé** : {real_interaction.channel.name}."
                )

            # Supprimer le canal
            print(f"Suppression du canal...")
            await real_interaction.channel.delete()
            print(f"Canal supprimé avec succès")

        except discord.errors.NotFound as e:
            print(f"Erreur NotFound lors de la fermeture du ticket: {e}")
            import traceback
            traceback.print_exc()
            # Le canal a peut-être déjà été supprimé, pas besoin de répondre

        except discord.errors.Forbidden as e:
            print(f"Erreur Forbidden lors de la fermeture du ticket: {e}")
            import traceback
            traceback.print_exc()
            try:
                if not real_interaction.response.is_done():
                    await real_interaction.response.send_message(
                        "❌ Je n'ai pas les permissions nécessaires pour fermer ce ticket. Contacte un admin !",
                        ephemeral=True)
            except Exception as inner_e:
                print(f"Erreur secondaire: {inner_e}")

        except Exception as e:
            print(f"Erreur lors de la fermeture du ticket: {e}")
            import traceback
            traceback.print_exc()
            try:
                if not real_interaction.response.is_done():
                    await real_interaction.response.send_message(
                        "❌ Une erreur s'est produite lors de la fermeture du ticket.",
                        ephemeral=True)
            except Exception as inner_e:
                print(f"Erreur secondaire: {inner_e}")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔰 Candidature staff",
                      style=discord.ButtonStyle.primary,
                      custom_id="ticket_category_staff")
    async def ticket_button_staff(self, button, interaction):
        print(f"=== Bouton staff cliqué ===")
        print(f"Type du premier paramètre: {type(button)}")
        print(f"Type du deuxième paramètre: {type(interaction)}")

        # Déterminer quel paramètre est l'interaction
        if isinstance(button, discord.Interaction):
            real_interaction = button
            print(f"L'interaction est le premier paramètre")
        elif isinstance(interaction, discord.Interaction):
            real_interaction = interaction
            print(f"L'interaction est le deuxième paramètre")
        else:
            print(f"Aucun paramètre n'est une interaction valide")
            return

        print(f"Utilisateur: {real_interaction.user.name if hasattr(real_interaction, 'user') and real_interaction.user else 'Non disponible'}")

        try:
            await self.create_ticket(real_interaction, "📌 Candidatures")
        except Exception as e:
            print(f"Erreur détaillée dans ticket_button_staff: {e}")
            import traceback
            traceback.print_exc()

    @discord.ui.button(label="💡 Besoin d'aide",
                      style=discord.ButtonStyle.primary,
                      custom_id="ticket_category_aide")
    async def ticket_button_aide(self, button, interaction):
        print(f"=== Bouton aide cliqué ===")
        print(f"Type du premier paramètre: {type(button)}")
        print(f"Type du deuxième paramètre: {type(interaction)}")

        # Déterminer quel paramètre est l'interaction
        if isinstance(button, discord.Interaction):
            real_interaction = button
            print(f"L'interaction est le premier paramètre")
        elif isinstance(interaction, discord.Interaction):
            real_interaction = interaction
            print(f"L'interaction est le deuxième paramètre")
        else:
            print(f"Aucun paramètre n'est une interaction valide")
            return

        print(f"Utilisateur: {real_interaction.user.name if hasattr(real_interaction, 'user') and real_interaction.user else 'Non disponible'}")

        try:
            await self.create_ticket(real_interaction, "❓ Aide")
        except Exception as e:
            print(f"Erreur détaillée dans ticket_button_aide: {e}")
            import traceback
            traceback.print_exc()

    @discord.ui.button(label="🚫 Demande de deban",
                      style=discord.ButtonStyle.primary,
                      custom_id="ticket_category_deban")
    async def ticket_button_deban(self, button, interaction):
        print(f"=== Bouton deban cliqué ===")
        print(f"Type du premier paramètre: {type(button)}")
        print(f"Type du deuxième paramètre: {type(interaction)}")

        # Déterminer quel paramètre est l'interaction
        if isinstance(button, discord.Interaction):
            real_interaction = button
            print(f"L'interaction est le premier paramètre")
        elif isinstance(interaction, discord.Interaction):
            real_interaction = interaction
            print(f"L'interaction est le deuxième paramètre")
        else:
            print(f"Aucun paramètre n'est une interaction valide")
            return

        print(f"Utilisateur: {real_interaction.user.name if hasattr(real_interaction, 'user') and real_interaction.user else 'Non disponible'}")

        try:
            await self.create_ticket(real_interaction, "🚫 Débannissement")
        except Exception as e:
            print(f"Erreur détaillée dans ticket_button_deban: {e}")
            import traceback
            traceback.print_exc()

    @discord.ui.button(label="🤝 Candidature partenaire",
                      style=discord.ButtonStyle.primary,
                      custom_id="ticket_category_partner")
    async def ticket_button_partner(self, button, interaction):
        print(f"=== Bouton partenaire cliqué ===")
        print(f"Type du premier paramètre: {type(button)}")
        print(f"Type du deuxième paramètre: {type(interaction)}")

        # Déterminer quel paramètre est l'interaction
        if isinstance(button, discord.Interaction):
            real_interaction = button
            print(f"L'interaction est le premier paramètre")
        elif isinstance(interaction, discord.Interaction):
            real_interaction = interaction
            print(f"L'interaction est le deuxième paramètre")
        else:
            print(f"Aucun paramètre n'est une interaction valide")
            return

        print(f"Utilisateur: {real_interaction.user.name if hasattr(real_interaction, 'user') and real_interaction.user else 'Non disponible'}")

        try:
            await self.create_ticket(real_interaction, "🤝 Partenariats")
        except Exception as e:
            print(f"Erreur détaillée dans ticket_button_partner: {e}")
            import traceback
            traceback.print_exc()

    @discord.ui.button(label="🚨 Plainte staff",
                      style=discord.ButtonStyle.danger,
                      custom_id="ticket_category_complaint")
    async def ticket_button_complaint(self, button, interaction):
        print(f"=== Bouton plainte staff cliqué ===")
        print(f"Type du premier paramètre: {type(button)}")
        print(f"Type du deuxième paramètre: {type(interaction)}")

        # Déterminer quel paramètre est l'interaction
        if isinstance(button, discord.Interaction):
            real_interaction = button
            print(f"L'interaction est le premier paramètre")
        elif isinstance(interaction, discord.Interaction):
            real_interaction = interaction
            print(f"L'interaction est le deuxième paramètre")
        else:
            print(f"Aucun paramètre n'est une interaction valide")
            return

        print(f"Utilisateur: {real_interaction.user.name if hasattr(real_interaction, 'user') and real_interaction.user else 'Non disponible'}")

        try:
            await self.create_ticket(real_interaction, "🚨 Plainte Staff")
        except Exception as e:
            print(f"Erreur détaillée dans ticket_button_complaint: {e}")
            import traceback
            traceback.print_exc()

    async def create_ticket(self, interaction, category_name: str):
        print(f"\n=== Création de ticket demandée ===")
        print(f"Catégorie: {category_name}")
        print(f"Type de l'interaction: {type(interaction)}")

        try:
            # Vérifier si l'objet interaction est valide
            if not interaction:
                print(f"Erreur: L'objet interaction est None")
                return

            # Vérifier si l'interaction a déjà été répondue
            try:
                is_done = interaction.response.is_done()
                print(f"L'interaction a déjà reçu une réponse: {is_done}")
                if is_done:
                    return
            except Exception as e:
                print(f"Erreur lors de la vérification de is_done(): {e}")
                return

            # Vérifier si les attributs nécessaires sont présents
            if not hasattr(interaction, 'user'):
                print("L'interaction n'a pas d'attribut 'user'")
                return

            if not hasattr(interaction, 'guild'):
                print("L'interaction n'a pas d'attribut 'guild'")
                return

            user = interaction.user
            guild = interaction.guild

            print(f"Utilisateur: {user.name} (ID: {user.id})")
            print(f"Serveur: {guild.name} (ID: {guild.id})")

            if not user or not guild:
                print(f"Erreur: Utilisateur ou serveur non disponible")
                await interaction.response.send_message(
                    "❌ Une erreur s'est produite. Réessaie plus tard.",
                    ephemeral=True)
                return

            # Rechercher la catégorie
            print(f"Recherche de la catégorie '{category_name}'...")
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                print(f"❌ Catégorie '{category_name}' non trouvée!")
                print(f"Catégories disponibles: {[c.name for c in guild.categories]}")
                await interaction.response.send_message(
                    f"❌ La catégorie `{category_name}` n'existe pas. Contacte un admin !",
                    ephemeral=True)
                return
            else:
                print(f"✅ Catégorie '{category_name}' trouvée (ID: {category.id})")

            # Vérifier si l'utilisateur a déjà un ticket dans cette catégorie
            print("Vérification des tickets existants...")
            existing_ticket = False
            for ticket_id, ticket_info in tickets.items():
                if ticket_info["creator_id"] == user.id and ticket_info["category"] == category_name:
                    existing_ticket = True
                    print(f"Ticket existant trouvé: {ticket_info['channel_name']} (ID: {ticket_id})")
                    channel = guild.get_channel(ticket_id)
                    if channel:
                        print(f"Canal existant: {channel.name}")
                        await interaction.response.send_message(
                            f"❌ Tu as déjà un ticket ouvert dans cette catégorie: {channel.mention}",
                            ephemeral=True)
                    else:
                        print(f"Le canal n'existe plus, suppression de l'entrée du dictionnaire")
                        del tickets[ticket_id]
                        existing_ticket = False
                    break

            if existing_ticket:
                return

            # Créer le ticket
            print(f"Création du canal ticket-{user.name}...")
            ticket_name = f"ticket-{user.name}"
            try:
                ticket_channel = await guild.create_text_channel(ticket_name, category=category)
                print(f"✅ Canal créé: {ticket_channel.name} (ID: {ticket_channel.id})")
            except Exception as e:
                print(f"❌ Erreur lors de la création du canal: {e}")
                await interaction.response.send_message(
                    "❌ Je n'ai pas pu créer le canal de ticket. Vérifie mes permissions.",
                    ephemeral=True)
                return

            # Stocker les informations du ticket dans le dictionnaire global
            print("Ajout du ticket au dictionnaire...")
            tickets[ticket_channel.id] = {
                "creator_id": user.id,
                "creator_name": user.name,
                "channel_id": ticket_channel.id,
                "channel_name": ticket_channel.name,
                "category": category_name,
                "members": [user.id]
            }
            print(f"✅ Ticket ajouté au dictionnaire")

            # Configurer les permissions
            print("Configuration des permissions...")
            try:
                await ticket_channel.set_permissions(guild.default_role, read_messages=False)
                await ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
                print(f"✅ Permissions de base configurées")
            except Exception as e:
                print(f"❌ Erreur lors de la configuration des permissions: {e}")

            # Donner accès aux administrateurs
            print(f"Recherche du rôle admin (ID: {ADMIN_ROLE_ID})...")
            admin_role = discord.utils.get(guild.roles, id=ADMIN_ROLE_ID)
            if admin_role:
                print(f"✅ Rôle admin trouvé: {admin_role.name}")
                try:
                    await ticket_channel.set_permissions(admin_role, read_messages=True, send_messages=True)
                    print(f"✅ Permissions admin configurées")
                except Exception as e:
                    print(f"❌ Erreur lors de la configuration des permissions admin: {e}")
            else:
                print(f"❌ Rôle admin non trouvé")

            # Envoyer un message dans le canal de logs
            print(f"Recherche du canal de logs (ID: {LOG_TICKET_ID})...")
            log_channel = discord.utils.get(guild.text_channels, id=LOG_TICKET_ID)
            if log_channel:
                print(f"✅ Canal de logs trouvé: {log_channel.name}")
                try:
                    await log_channel.send(
                        f"🔓 **Ouverture de ticket**\n**Utilisateur** : {user.mention} ({user.id})\n**Ticket créé** : {ticket_channel.mention} dans la catégorie `{category_name}`."
                    )
                    print(f"✅ Message de log envoyé")
                except Exception as e:
                    print(f"❌ Erreur lors de l'envoi du message de log: {e}")
            else:
                print(f"❌ Canal de logs non trouvé")

            # Créer une instance de la vue de fermeture avec l'ID du créateur
            print("Création de la vue de fermeture...")
            close_view = CloseTicketView(user.id)

            # Envoyer un message dans le canal de ticket
            print("Envoi du message de bienvenue dans le ticket...")
            try:
                await ticket_channel.send(
                    f"👋 Salut {user.mention}, ton ticket a été créé dans la catégorie `{category_name}`.\nUtilise le bouton ci-dessous pour fermer ce ticket une fois ton problème résolu.",
                    view=close_view)
                print(f"✅ Message de bienvenue envoyé")
            except Exception as e:
                print(f"❌ Erreur lors de l'envoi du message de bienvenue: {e}")

            # Répondre à l'interaction
            print("Envoi de la réponse à l'interaction...")
            try:
                await interaction.response.send_message(
                    f"✅ Ton ticket a été créé : {ticket_channel.mention}",
                    ephemeral=True)
                print(f"✅ Réponse à l'interaction envoyée")
            except Exception as e:
                print(f"❌ Erreur lors de l'envoi de la réponse à l'interaction: {e}")

            print("=== Création de ticket terminée avec succès ===\n")

        except discord.errors.NotFound as e:
            print(f"Erreur NotFound lors de la création du ticket: {e}")
            import traceback
            traceback.print_exc()
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ Une erreur s'est produite: ressource introuvable. Contacte un admin !",
                        ephemeral=True)
            except Exception as inner_e:
                print(f"Erreur secondaire: {inner_e}")

        except discord.errors.Forbidden as e:
            print(f"Erreur Forbidden lors de la création du ticket: {e}")
            import traceback
            traceback.print_exc()
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ Je n'ai pas les permissions nécessaires pour créer ce ticket. Contacte un admin !",
                        ephemeral=True)
            except Exception as inner_e:
                print(f"Erreur secondaire: {inner_e}")

        except Exception as e:
            print(f"Erreur lors de la création du ticket: {e}")
            import traceback
            traceback.print_exc()
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ Une erreur s'est produite lors de la création du ticket. Contacte un admin !",
                        ephemeral=True)
            except Exception as inner_e:
                print(f"Erreur secondaire: {inner_e}")

# Commandes pour renommer et gérer les membres des tickets
@bot.command(name="renameticket")
async def rename_ticket(ctx, *, nouveau_nom: str):
    """Renomme le ticket actuel."""
    # Vérifier si le canal est un ticket
    if not ctx.channel.name.startswith("ticket-"):
        await ctx.send("❌ Cette commande ne peut être utilisée que dans un canal de ticket.")
        return

    # Vérifier si le ticket est dans notre dictionnaire
    if ctx.channel.id not in tickets:
        # Si le ticket n'est pas dans le dictionnaire, vérifier les permissions
        if not ctx.author.guild_permissions.manage_channels:
            await ctx.send("❌ Tu n'as pas la permission de renommer ce ticket.")
            return
    else:
        # Si le ticket est dans le dictionnaire, vérifier si l'utilisateur est le créateur ou un admin
        if ctx.author.id != tickets[ctx.channel.id]["creator_id"] and not ctx.author.guild_permissions.manage_channels:
            await ctx.send("❌ Tu n'as pas la permission de renommer ce ticket.")
            return

    # Renommer le canal
    try:
        await ctx.channel.edit(name=f"ticket-{nouveau_nom}")

        # Mettre à jour le dictionnaire si le ticket y est
        if ctx.channel.id in tickets:
            tickets[ctx.channel.id]["channel_name"] = f"ticket-{nouveau_nom}"

        await ctx.send(f"✅ Le ticket a été renommé en `ticket-{nouveau_nom}`.")

        # Log de l'action
        log_channel = discord.utils.get(ctx.guild.text_channels, id=LOG_TICKET_ID)
        if log_channel:
            await log_channel.send(
                f"🔄 **Ticket renommé**\n**Utilisateur** : {ctx.author.mention} ({ctx.author.id})\n**Ticket** : {ctx.channel.mention}\n**Nouveau nom** : `ticket-{nouveau_nom}`"
            )
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de renommer ce canal.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Une erreur s'est produite lors du renommage du canal : {e}")

@bot.command(name="addmember")
async def add_member(ctx, member: discord.Member):
    """Ajoute un membre au ticket actuel."""
    # Vérifier si le canal est un ticket
    if not ctx.channel.name.startswith("ticket-"):
        await ctx.send("❌ Cette commande ne peut être utilisée que dans un canal de ticket.")
        return

    # Vérifier si le ticket est dans notre dictionnaire
    if ctx.channel.id not in tickets:
        # Si le ticket n'est pas dans le dictionnaire, vérifier les permissions
        if not ctx.author.guild_permissions.manage_channels:
            await ctx.send("❌ Tu n'as pas la permission d'ajouter des membres à ce ticket.")
            return
    else:
        # Si le ticket est dans le dictionnaire, vérifier si l'utilisateur est le créateur ou un admin
        if ctx.author.id != tickets[ctx.channel.id]["creator_id"] and not ctx.author.guild_permissions.manage_channels:
            await ctx.send("❌ Tu n'as pas la permission d'ajouter des membres à ce ticket.")
            return

    # Ajouter le membre au ticket
    try:
        await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)

        # Mettre à jour le dictionnaire si le ticket y est
        if ctx.channel.id in tickets and member.id not in tickets[ctx.channel.id]["members"]:
            tickets[ctx.channel.id]["members"].append(member.id)

        await ctx.send(f"✅ {member.mention} a été ajouté au ticket.")

        # Log de l'action
        log_channel = discord.utils.get(ctx.guild.text_channels, id=LOG_TICKET_ID)
        if log_channel:
            await log_channel.send(
                f"➕ **Membre ajouté au ticket**\n**Utilisateur** : {ctx.author.mention} ({ctx.author.id})\n**Membre ajouté** : {member.mention} ({member.id})\n**Ticket** : {ctx.channel.mention}"
            )
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de modifier les permissions de ce canal.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Une erreur s'est produite lors de l'ajout du membre : {e}")

@bot.command(name="removemember")
async def remove_member(ctx, member: discord.Member):
    """Retire un membre du ticket actuel."""
    # Vérifier si le canal est un ticket
    if not ctx.channel.name.startswith("ticket-"):
        await ctx.send("❌ Cette commande ne peut être utilisée que dans un canal de ticket.")
        return

    # Vérifier si le ticket est dans notre dictionnaire
    if ctx.channel.id not in tickets:
        # Si le ticket n'est pas dans le dictionnaire, vérifier les permissions
        if not ctx.author.guild_permissions.manage_channels:
            await ctx.send("❌ Tu n'as pas la permission de retirer des membres de ce ticket.")
            return
    else:
        # Si le ticket est dans le dictionnaire, vérifier si l'utilisateur est le créateur ou un admin
        if ctx.author.id != tickets[ctx.channel.id]["creator_id"] and not ctx.author.guild_permissions.manage_channels:
            await ctx.send("❌ Tu n'as pas la permission de retirer des membres de ce ticket.")
            return

        # Vérifier que le membre n'est pas le créateur du ticket
        if member.id == tickets[ctx.channel.id]["creator_id"]:
            await ctx.send("❌ Tu ne peux pas retirer le créateur du ticket.")
            return

    # Vérifier que le membre n'est pas un administrateur
    if member.guild_permissions.administrator and not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu ne peux pas retirer un administrateur du ticket.")
        return

    # Retirer le membre du ticket
    try:
        await ctx.channel.set_permissions(member, overwrite=None)

        # Mettre à jour le dictionnaire si le ticket y est
        if ctx.channel.id in tickets and member.id in tickets[ctx.channel.id]["members"]:
            tickets[ctx.channel.id]["members"].remove(member.id)

        await ctx.send(f"✅ {member.mention} a été retiré du ticket.")

        # Log de l'action
        log_channel = discord.utils.get(ctx.guild.text_channels, id=LOG_TICKET_ID)
        if log_channel:
            await log_channel.send(
                f"➖ **Membre retiré du ticket**\n**Utilisateur** : {ctx.author.mention} ({ctx.author.id})\n**Membre retiré** : {member.mention} ({member.id})\n**Ticket** : {ctx.channel.mention}"
            )
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de modifier les permissions de ce canal.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Une erreur s'est produite lors du retrait du membre : {e}")

@bot.command(name="listtickets")
async def list_tickets(ctx):
    """Liste tous les tickets actifs."""
    # Vérifier les permissions avec le nouveau système
    if not has_permission(ctx.author, "listtickets"):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if not tickets:
        await ctx.send("📝 Aucun ticket actif pour le moment.")
        return

    # Créer un embed pour afficher les tickets
    embed = discord.Embed(
        title="📝 Liste des tickets actifs",
        color=discord.Color.blue(),
        description=f"Il y a actuellement {len(tickets)} ticket(s) actif(s)."
    )

    for ticket_id, ticket_info in tickets.items():
        creator = ctx.guild.get_member(ticket_info["creator_id"])
        creator_name = creator.name if creator else ticket_info["creator_name"]

        # Obtenir les noms des membres
        members = []
        for member_id in ticket_info["members"]:
            member = ctx.guild.get_member(member_id)
            if member:
                members.append(member.name)

        members_str = ", ".join(members) if members else "Aucun"

        # Ajouter un champ pour ce ticket
        embed.add_field(
            name=f"🎫 {ticket_info['channel_name']}",
            value=f"**Créateur:** {creator_name}\n"
                  f"**Catégorie:** {ticket_info['category']}\n"
                  f"**Membres:** {members_str}\n"
                  f"**Lien:** <#{ticket_id}>",
            inline=False
        )

    await ctx.send(embed=embed)

class Ticket:
    def __init__(self, id_ticket, nom, membres=None):
        self.id_ticket = id_ticket
        self.nom = nom
        self.membres = membres if membres else []

    def rename_ticket(self, nouveau_nom):
        """Renomme le ticket."""
        self.nom = nouveau_nom
        print(f"Le ticket {self.id_ticket} a été renommé en '{self.nom}'.")

    def ajouter_membre(self, membre):
        """Ajoute un membre au ticket."""
        if membre not in self.membres:
            self.membres.append(membre)
            print(f"{membre} a été ajouté au ticket {self.id_ticket}.")
        else:
            print(f"{membre} est déjà membre du ticket {self.id_ticket}.")

    def retirer_membre(self, membre):
        """Retire un membre du ticket."""
        if membre in self.membres:
            self.membres.remove(membre)
            print(f"{membre} a été retiré du ticket {self.id_ticket}.")
        else:
            print(f"{membre} n'est pas membre du ticket {self.id_ticket}.")

# Exemple d'utilisation
ticket1 = Ticket(1, "Bug Interface", ["Alice", "Bob"])
ticket1.rename_ticket("Correction Interface")
ticket1.ajouter_membre("Charlie")
ticket1.retirer_membre("Alice")

# Événements du bot
@bot.event
async def on_ready():
    print(f"{bot.user.name} est connecté !")

    # Afficher toutes les commandes enregistrées pour le débogage
    commands_list = [command.name for command in bot.commands]
    print(f"Commandes enregistrées: {', '.join(commands_list)}")

    # Charger et mettre à jour le règlement
    await update_reglement_on_startup()

    # Vérifier les serveurs et leurs configurations
    for guild in bot.guilds:
        print(f"\n=== Vérification du serveur: {guild.name} (ID: {guild.id}) ===")

        # Vérifier les catégories
        categories = ["📌 Candidatures", "❓ Aide", "🚫 Débannissement", "🤝 Partenariats", "🚨 Plainte Staff"]
        for cat_name in categories:
            category = discord.utils.get(guild.categories, name=cat_name)
            print(f"  Catégorie '{cat_name}': {'✅ Trouvée' if category else '❌ MANQUANTE'}")

        # Vérifier les canaux importants
        log_channel = discord.utils.get(guild.text_channels, id=LOG_CHANNEL_ID)
        log_ticket = discord.utils.get(guild.text_channels, id=LOG_TICKET_ID)
        support_channel = discord.utils.get(guild.text_channels, name="ticket-support")

        print(f"  Canal de logs général (ID: {LOG_CHANNEL_ID}): {'✅ Trouvé' if log_channel else '❌ MANQUANT'}")
        print(f"  Canal de logs tickets (ID: {LOG_TICKET_ID}): {'✅ Trouvé' if log_ticket else '❌ MANQUANT'}")
        print(f"  Canal ticket-support: {'✅ Trouvé' if support_channel else '❌ MANQUANT'}")

        # Vérifier les rôles
        mute_role = discord.utils.get(guild.roles, id=MUTE_ROLE_ID)
        owner_role = discord.utils.get(guild.roles, id=OWNER_ROLE_ID)
        admin_role = discord.utils.get(guild.roles, id=ADMIN_ROLE_ID)
        mod_role = discord.utils.get(guild.roles, id=MOD_ROLE_ID)
        helper_role = discord.utils.get(guild.roles, id=HELPER_ROLE_ID)
        join_role = discord.utils.get(guild.roles, id=ROLE_JOIN_ID)
        giveaway_role = discord.utils.get(guild.roles, id=GIVEAWAY_WINNER_ROLE_ID)

        print(f"  Rôle mute (ID: {MUTE_ROLE_ID}): {'✅ Trouvé' if mute_role else '❌ MANQUANT'}")
        print(f"  Rôle propriétaire (ID: {OWNER_ROLE_ID}): {'✅ Trouvé' if owner_role else '❌ MANQUANT'}")
        print(f"  Rôle administrateur (ID: {ADMIN_ROLE_ID}): {'✅ Trouvé' if admin_role else '❌ MANQUANT'}")
        print(f"  Rôle modérateur (ID: {MOD_ROLE_ID}): {'✅ Trouvé' if mod_role else '❌ MANQUANT'}")
        print(f"  Rôle helper (ID: {HELPER_ROLE_ID}): {'✅ Trouvé' if helper_role else '❌ MANQUANT'}")
        print(f"  Rôle join (ID: {ROLE_JOIN_ID}): {'✅ Trouvé' if join_role else '❌ MANQUANT'}")
        print(f"  Rôle giveaway (ID: {GIVEAWAY_WINNER_ROLE_ID}): {'✅ Trouvé' if giveaway_role else '❌ MANQUANT'}")

    if not bot.persistent_views_added:
        try:
            # Ajouter la vue des tickets
            print("Tentative d'ajout de la vue des tickets...")
            bot.add_view(TicketView())
            print("Vue des tickets ajoutée avec succès")

            # Ajouter une vue générique pour les boutons de fermeture
            # Utiliser None comme creator_id pour que les admins puissent toujours fermer
            print("Tentative d'ajout de la vue de fermeture de ticket...")
            bot.add_view(CloseTicketView(None))
            print("Vue de fermeture de ticket ajoutée avec succès")

            # Ajouter une vue générique pour les boutons de vérification par règlement
            print("Tentative d'ajout de la vue de vérification par règlement...")
            bot.add_view(ReglementVerificationView())
            print("Vue de vérification par règlement ajoutée avec succès")

            bot.persistent_views_added = True

            # Vérifier si un message de règlement existe et le mettre à jour
            try:
                # Mettre à jour le message de règlement dans tous les serveurs
                for guild in bot.guilds:
                    await update_reglement_message(guild)
                    print(f"Message de règlement mis à jour pour le serveur {guild.name}")
            except Exception as e:
                print(f"Erreur lors de la mise à jour du message de règlement: {e}")
                import traceback
                traceback.print_exc()

        except Exception as e:
            print(f"Erreur détaillée lors de l'ajout des vues persistantes: {e}")
            import traceback
            traceback.print_exc()

        # Rechercher les canaux de ticket existants et les ajouter au dictionnaire
        print("\n=== Recherche des tickets existants ===")
        for guild in bot.guilds:
            print(f"Recherche dans le serveur: {guild.name}")
            for channel in guild.text_channels:
                if channel.name.startswith("ticket-"):
                    print(f"Canal de ticket trouvé: {channel.name} (ID: {channel.id})")
                    # Essayer de trouver le créateur du ticket
                    creator_id = None
                    creator_name = "Inconnu"
                    members = []

                    # Vérifier les permissions pour trouver le créateur et les membres
                    for target, permissions in channel.overwrites.items():
                        if isinstance(target, discord.Member) and permissions.read_messages:
                            if creator_id is None:
                                creator_id = target.id
                                creator_name = target.name
                                print(f"  Créateur probable: {creator_name} (ID: {creator_id})")
                            members.append(target.id)

                    # Ajouter le ticket au dictionnaire
                    if creator_id:
                        tickets[channel.id] = {
                            "creator_id": creator_id,
                            "creator_name": creator_name,
                            "channel_id": channel.id,
                            "channel_name": channel.name,
                            "category": channel.category.name if channel.category else "Sans catégorie",
                            "members": members
                        }
                        print(f"  Ticket ajouté au dictionnaire: {channel.name}")
                        print(f"  Membres: {len(members)}")
                    else:
                        print(f"  Aucun créateur trouvé pour ce ticket, il ne sera pas ajouté")

    # Rechercher les canaux de support pour les tickets
    print("\n=== Configuration des canaux de support ===")
    for guild in bot.guilds:
        print(f"Recherche du canal de support dans: {guild.name}")
        support_channel = discord.utils.get(guild.text_channels, name="ticket-support")
        if support_channel:
            print(f"Canal ticket-support trouvé: {support_channel.name} (ID: {support_channel.id})")
            try:
                has_ticket_message = False
                print("Recherche des messages existants...")
                async for message in support_channel.history(limit=100):
                    if message.author == bot.user and "Choisis une catégorie pour ton ticket" in message.content:
                        has_ticket_message = True
                        print(f"Message de ticket trouvé (ID: {message.id})")
                        # S'assurer que la vue est attachée au message
                        try:
                            print(f"Tentative d'ajout de la vue au message existant...")
                            bot.add_view(TicketView(), message_id=message.id)
                            print(f"Vue ajoutée avec succès au message existant dans {guild.name}")
                        except Exception as e:
                            print(f"Erreur lors de l'ajout de la vue au message existant dans {guild.name}: {e}")
                            import traceback
                            traceback.print_exc()
                        break

                if not has_ticket_message:
                    print(f"Aucun message de ticket trouvé dans {guild.name}.")
                    print(f"Utilisez la commande !ticket ou !setuptickets pour créer un message de ticket.")
            except Exception as e:
                print(f"Erreur lors de la recherche des messages de ticket dans {guild.name}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ ATTENTION: Canal ticket-support non trouvé dans {guild.name}")

    print("\n=== Initialisation terminée ===")
    print(f"Bot prêt à l'emploi sur {len(bot.guilds)} serveurs")

@bot.event
async def on_member_join(member):
    """Gère l'arrivée d'un nouveau membre : log de l'arrivée."""
    print(f"Nouvel utilisateur rejoint : {member.name} (ID: {member.id})")

    try:
        # Log de l'arrivée du membre dans le canal général
        log_channel = bot.get_channel(LOG_FLUX_ID)
        if log_channel:
            welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
            channel_mention = welcome_channel.mention if welcome_channel else "le canal de bienvenue"

            await log_channel.send(
                f"📥 **Nouveau membre** : {member.mention} ({member.id}) a rejoint le serveur. "
                f"L'utilisateur doit se rendre dans {channel_mention} pour se vérifier."
            )

        # Log de l'arrivée dans le canal dédié aux arrivées/départs
        join_leave_channel = bot.get_channel(LOG_JOIN_LEAVE_ID)
        if join_leave_channel:
            # Créer un embed pour l'arrivée
            embed = discord.Embed(
                title="📥 Nouveau membre",
                description=f"{member.mention} a rejoint le serveur.",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )

            # Ajouter des informations sur l'utilisateur
            embed.add_field(name="ID", value=str(member.id), inline=True)
            embed.add_field(name="Nom", value=member.name, inline=True)

            # Ajouter la date de création du compte
            created_at = member.created_at.strftime("%d/%m/%Y %H:%M:%S")
            embed.add_field(name="Compte créé le", value=created_at, inline=True)

            # Ajouter l'avatar de l'utilisateur
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)

            # Ajouter un pied de page
            embed.set_footer(text=f"Membres: {member.guild.member_count}")

            await join_leave_channel.send(embed=embed)

    except Exception as e:
        print(f"Erreur lors du log de l'arrivée du membre : {e}")
        import traceback
        traceback.print_exc()

        # Log de l'erreur
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"⚠️ **Erreur** : Impossible de logger l'arrivée de {member.mention}. Erreur: {str(e)}")

@bot.event
async def on_member_remove(member):
    """Gère le départ d'un membre : log du départ."""
    print(f"Utilisateur parti : {member.name} (ID: {member.id})")

    try:
        # Log du départ dans le canal général
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"📤 **Membre parti** : {member.mention} ({member.id}) a quitté le serveur."
            )

        # Log du départ dans le canal dédié aux arrivées/départs
        join_leave_channel = bot.get_channel(LOG_JOIN_LEAVE_ID)
        if join_leave_channel:
            # Créer un embed pour le départ
            embed = discord.Embed(
                title="📤 Membre parti",
                description=f"{member.mention} a quitté le serveur.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            # Ajouter des informations sur l'utilisateur
            embed.add_field(name="ID", value=str(member.id), inline=True)
            embed.add_field(name="Nom", value=member.name, inline=True)

            # Calculer la durée de présence sur le serveur
            joined_at = member.joined_at
            if joined_at:
                joined_str = joined_at.strftime("%d/%m/%Y %H:%M:%S")
                # Calculer la durée en jours
                duration = (discord.utils.utcnow() - joined_at).days
                duration_str = f"{duration} jour(s)"
                embed.add_field(name="Présent depuis", value=f"{joined_str} ({duration_str})", inline=True)

            # Ajouter l'avatar de l'utilisateur
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)

            # Ajouter un pied de page
            embed.set_footer(text=f"Membres restants: {member.guild.member_count}")

            await join_leave_channel.send(embed=embed)

    except Exception as e:
        print(f"Erreur lors du log du départ du membre : {e}")
        import traceback
        traceback.print_exc()

        # Log de l'erreur
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"⚠️ **Erreur** : Impossible de logger le départ de {member.name} (ID: {member.id}). Erreur: {str(e)}")

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    # Vérifier si la réaction est pour un giveaway
    for giveaway_id, giveaway_data in list(giveaways.items()):
        if reaction.message.id == giveaway_id and str(reaction.emoji) == "🎉":
            giveaway_data["participants"].add(user)
            print(f"{user.name} a participé au giveaway.")



       
    # Vérifier si l'utilisateur a un rôle de staff (propriétaire ou administrateur)
    owner_role = discord.utils.get(message.author.roles, id=OWNER_ROLE_ID)
    admin_role = discord.utils.get(message.author.roles, id=ADMIN_ROLE_ID)
    is_staff = owner_role is not None or admin_role is not None

    # Vérification des mots interdits
    for mot in MOTS_INTERDITS:
        if mot in message.content.lower():
            # Supprimer le message pour tout le monde (y compris les admins)
            try:
                await message.delete()
            except discord.errors.NotFound:
                # Le message a déjà été supprimé ou n'existe plus
                print(f"Message introuvable lors de la tentative de suppression.")
                pass
            except discord.errors.Forbidden:
                # Le bot n'a pas la permission de supprimer le message
                print(f"Permission refusée lors de la tentative de suppression d'un message.")
                pass
            except Exception as e:
                # Autre erreur
                print(f"Erreur lors de la suppression du message: {e}")
                pass

            # Appliquer les avertissements seulement pour les non-staff (ni propriétaire ni administrateur)
            if not is_staff:
                if message.author.id not in warnings:
                    warnings[message.author.id] = 0

                warnings[message.author.id] += 1

                await message.channel.send(f"{message.author.mention}, attention ! Ce mot est interdit. Avertissement {warnings[message.author.id]}/3")

                if warnings[message.author.id] >= 3:
                    try:
                        await message.author.kick(reason="Trop d'avertissements pour langage inapproprié.")
                        await message.channel.send(f"{message.author.mention} a été expulsé pour non-respect des règles.")
                    except discord.errors.Forbidden:
                        await message.channel.send(f"Je n'ai pas la permission d'expulser {message.author.mention}.")
                        print(f"Permission refusée lors de la tentative d'expulsion de {message.author.name}.")
                    except Exception as e:
                        print(f"Erreur lors de l'expulsion de {message.author.name}: {e}")

                # Ne pas traiter les commandes si un mot interdit a été détecté pour les non-staff
                return

            # Pour les staff (propriétaires et admins), on continue le traitement des commandes après suppression du message
            break
    
    # Permettre le traitement des commandes
    await bot.process_commands(message)

# Commandes générales
@bot.command()
async def hello(ctx):
    # Vérifier si l'utilisateur a un rôle de staff (propriétaire, admin, mod ou helper)
    owner_role = discord.utils.get(ctx.author.roles, id=OWNER_ROLE_ID)
    admin_role = discord.utils.get(ctx.author.roles, id=ADMIN_ROLE_ID)
    mod_role = discord.utils.get(ctx.author.roles, id=MOD_ROLE_ID)
    helper_role = discord.utils.get(ctx.author.roles, id=HELPER_ROLE_ID)

    if not any([owner_role, admin_role, mod_role, helper_role]):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return
    await ctx.send(
        "Salut ! Je suis là pour t'aider. Utilise !commands pour voir toutes les commandes."
    )

@bot.command()
async def commands(ctx):
    """Affiche la liste de toutes les commandes disponibles."""
    # Vérifier si l'utilisateur a un rôle de staff (propriétaire, admin, mod ou helper)
    owner_role = discord.utils.get(ctx.author.roles, id=OWNER_ROLE_ID)
    admin_role = discord.utils.get(ctx.author.roles, id=ADMIN_ROLE_ID)
    mod_role = discord.utils.get(ctx.author.roles, id=MOD_ROLE_ID)
    helper_role = discord.utils.get(ctx.author.roles, id=HELPER_ROLE_ID)

    if not any([owner_role, admin_role, mod_role, helper_role]):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Créer un embed pour afficher les commandes
    embed = discord.Embed(
        title="📋 Liste des commandes",
        description="Voici la liste des commandes disponibles sur ce serveur :",
        color=0x3498db
    )

    # Commandes générales
    general_commands = [
        "`!hello` - Le bot répond avec un message sympa",
        "`!commands` - Affiche cette liste de commandes",
        "`!serverinfo` - Afficher les informations du serveur",
        "`!userinfo [@utilisateur]` - Afficher les informations d'un utilisateur",
        "`!avatar [@utilisateur]` - Afficher l'avatar d'un utilisateur",
        "`!checksetup` - Vérifie si le serveur est correctement configuré",
        "`!setjoinleavechannel [#canal]` - Configure le canal pour les logs d'arrivées et départs"
    ]
    embed.add_field(name="🎉 Général", value="\n".join(general_commands), inline=False)

    # Commandes de gestion des rôles de staff - divisées en plusieurs parties pour éviter de dépasser la limite de 1024 caractères
    staff_commands_1 = [
        "`!setownerrole @role` - Définit le rôle propriétaire du serveur",
        "`!setadminrole @role` - Définit le rôle administrateur",
        "`!setmodrole @role` - Définit le rôle modérateur",
        "`!sethelperrole @role` - Définit le rôle helper",
        "`!createrole <nom> <couleur> commandes...` - Crée un nouveau rôle Discord",
        "`!setrole <nom> <@role ou nom> commandes...` - Configure un rôle existant",
        "`!listroles` - Affiche tous les rôles configurés",
        "`!delrole <nom ou @mention>` - Supprime un rôle Discord du serveur"
    ]

    staff_commands_2 = [
        "`!addrolecommand <nom ou @mention> commandes...` - Ajoute des commandes à un rôle",
        "`!removerolecommand <nom ou @mention> commandes...` - Retire des commandes d'un rôle",
        "`!staffperms [owner/admin/mod/helper]` - Affiche les permissions détaillées du staff",
        "`!permissions [nom ou @mention]` - Affiche les permissions d'un rôle",
        "`!perms [nom ou @mention]` - Alias de permissions",
        "`!addperm <nom ou @mention> <commande>` - Ajoute une permission à un rôle",
        "`!removeperm <nom ou @mention> <commande>` - Retire une permission d'un rôle",
        "`!resetperms [mod/helper/all]` - Réinitialise les permissions"
    ]

    # N'afficher les commandes de gestion des rôles de staff qu'aux propriétaires et administrateurs
    if owner_role or admin_role:
        embed.add_field(name="👑 Gestion des rôles (1/2)", value="\n".join(staff_commands_1), inline=False)
        embed.add_field(name="👑 Gestion des rôles (2/2)", value="\n".join(staff_commands_2), inline=False)

    # Commandes de modération
    mod_commands = [
        "`!ban @utilisateur [raison]` - Bannir un utilisateur",
        "`!unban ID_utilisateur` - Débannir un utilisateur",
        "`!kick @utilisateur [raison]` - Expulser un utilisateur",
        "`!mute @utilisateur [durée] [raison]` - Rendre muet un utilisateur",
        "`!unmute @utilisateur` - Rendre la parole à un utilisateur",
        "`!clear [nombre]` - Supprimer des messages",
        "`!warn @utilisateur [raison]` - Avertir un utilisateur",
        "`!warnings @utilisateur` - Voir les avertissements d'un utilisateur",
        "`!clearwarns @utilisateur` - Effacer les avertissements d'un utilisateur",
        "`!addword <mot>` - Ajouter un mot à la liste des mots interdits",
        "`!removeword <mot>` - Retirer un mot de la liste des mots interdits",
        "`!listwords` - Afficher la liste des mots interdits"
    ]
    embed.add_field(name="🛡️ Modération", value="\n".join(mod_commands), inline=False)

    # Commandes de rôles
    role_commands = [
        "`!addrole @utilisateur @rôle` - Ajouter un rôle à un utilisateur",
        "`!removerole @utilisateur @rôle` - Retirer un rôle à un utilisateur"
    ]
    embed.add_field(name="🏷️ Gestion des rôles", value="\n".join(role_commands), inline=False)

    # Commandes de tickets
    ticket_commands = [
        "`!setuptickets` - Configurer le système de tickets",
        "`!resetticket` - Recréer le message de ticket dans le canal ticket-support",
        "`!ticket` - Crée un message de création de ticket",
        "`!renameticket <nouveau_nom>` - Renomme un ticket",
        "`!addmember @utilisateur` - Ajoute un membre au ticket",
        "`!removemember @utilisateur` - Retire un membre du ticket",
        "`!listtickets` - Affiche la liste des tickets actifs"
    ]
    embed.add_field(name="🎫 Système de tickets", value="\n".join(ticket_commands), inline=False)

    # Commandes de vérification par règlement
    verification_commands = [
        "`!showrules` - Afficher le règlement avec un bouton pour accepter et obtenir le rôle membre"
    ]
    embed.add_field(name="✅ Système de vérification", value="\n".join(verification_commands), inline=False)

    # Note: Les commandes suivantes ne sont pas encore implémentées ou sont en cours de développement

    # Commandes de règlement
    reglement_commands = [
        "`!setupreglement [#canal]` - Configurer le canal de règlement",
        "`!addrule <texte>` - Ajouter une règle au règlement",
        "`!removerule <numéro>` - Supprimer une règle du règlement",
        "`!editrule <numéro> <texte>` - Modifier une règle existante",
        "`!showrules` - Afficher la liste des règles",
        "`!setbanner [url]` - Changer la bannière du règlement",
        "`!resetrules` - Supprimer toutes les règles"
    ]
    embed.add_field(name="📜 Règlement", value="\n".join(reglement_commands), inline=False)

    # Pied de page
    embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    # Envoyer l'embed
    await ctx.send(embed=embed)

@bot.command()
async def ticket(ctx):
    """Crée un message de création de ticket dans le canal ticket-support."""
    # Vérifier si l'utilisateur a un rôle de staff (propriétaire ou administrateur)
    owner_role = discord.utils.get(ctx.author.roles, id=OWNER_ROLE_ID)
    admin_role = discord.utils.get(ctx.author.roles, id=ADMIN_ROLE_ID)

    if not (owner_role or admin_role):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    support_channel = discord.utils.get(ctx.guild.text_channels,
                                      name="ticket-support")
    if not support_channel:
        await ctx.send(
            "❌ Aucun canal 'ticket-support' trouvé. Créez ce canal avant d'utiliser cette commande."
        )
        return

    view = TicketView()
    await support_channel.send("📝 **Choisis une catégorie pour ton ticket :**",
                              view=view)
    await ctx.send(
        f"✅ Message de création de ticket ajouté dans {support_channel.mention}"
    )

# La commande resetticket a été supprimée ici car elle est déjà définie plus loin dans le code (ligne ~1758)

@bot.command()
async def giveaway(ctx, time: int, *, prize: str):
    role = discord.utils.get(ctx.author.roles, id=ADMIN_ROLE_ID)
    if role is None:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Vérifier s'il y a déjà un giveaway en cours
    if any(giveaways):
        await ctx.send("❌ Un giveaway est déjà en cours !")
        return

    giveaway_msg = await ctx.send(f"🎉 **GIVEAWAY** 🎉\n"
                                  f"🏆 Prix : {prize}\n"
                                  f"🕒 Temps restant : {time} secondes.\n"
                                  f"Réagis avec 🎉 pour participer !")

    await giveaway_msg.add_reaction("🎉")

    # Stocker les informations du giveaway avec l'ID du message comme clé
    giveaways[giveaway_msg.id] = {
        "prize": prize,
        "time": time,
        "message": giveaway_msg,
        "participants": set()
    }

    # Compte à rebours du giveaway
    remaining_time = time
    while remaining_time > 0:
        remaining_time -= 1
        await asyncio.sleep(1)
        if remaining_time % 10 == 0 or remaining_time <= 5:
            await giveaway_msg.edit(content=f"🎉 **GIVEAWAY** 🎉\n"
                                    f"🏆 Prix : {prize}\n"
                                    f"🕒 Temps restant : {remaining_time} secondes.\n"
                                    f"Réagis avec 🎉 pour participer !")

    # Vérifier s'il y a des participants et choisir un gagnant
    current_giveaway = giveaways.get(giveaway_msg.id)
    if current_giveaway and current_giveaway["participants"]:
        winner = random.choice(list(current_giveaway["participants"]))
        await giveaway_msg.edit(
            content=f"🎉 **GIVEAWAY TERMINÉ !** 🎉\n"
            f"🏆 **Le gagnant est {winner.mention} !** 🎊\n    "
            f"🎁 Prix remporté : {prize}")

        # Ajout et retrait de rôles au gagnant
        role_to_remove = discord.utils.get(winner.guild.roles,
                                         id=ROLE_JOIN_ID)
        role_to_add = discord.utils.get(winner.guild.roles,
                                      id=GIVEAWAY_WINNER_ROLE_ID)

        if role_to_remove and role_to_add:
            try:
                # Vérifier si le rôle du bot est plus haut dans la hiérarchie
                bot_member = winner.guild.get_member(bot.user.id)
                bot_top_role = bot_member.top_role

                if bot_top_role.position <= role_to_remove.position or bot_top_role.position <= role_to_add.position:
                    error_msg = f"Erreur : Le rôle du bot ({bot_top_role.name}) est plus bas que les rôles à modifier."
                    print(error_msg)
                    await ctx.send(f"⚠️ **Erreur de permission** : {error_msg}")
                    return

                await winner.remove_roles(role_to_remove)
                await winner.add_roles(role_to_add)
                print(
                    f"Le rôle {role_to_remove.name} a été retiré et {role_to_add.name} ajouté à {winner.name}."
                )
                await ctx.send(f"🏆 Les rôles de {winner.mention} ont été mis à jour !")
            except discord.Forbidden:
                error_msg = f"Erreur : Le bot n'a pas la permission de modifier les rôles de {winner.name}."
                print(error_msg)
                await ctx.send(f"⚠️ **Erreur de permission** : {error_msg} Vérifiez que le bot a la permission 'Gérer les rôles'.")
            except Exception as e:
                error_msg = f"Erreur inconnue lors de la modification des rôles : {e}"
                print(error_msg)
                await ctx.send(f"⚠️ **Erreur** : {error_msg}")
    else:
        await giveaway_msg.edit(
            content=f"🎉 **GIVEAWAY TERMINÉ !** 🎉\n"
            f"Aucun participant pour le giveaway de **{prize}**.\n"
            f"Le giveaway est annulé.")

    # Supprimer les informations du giveaway
    if giveaway_msg.id in giveaways:
        del giveaways[giveaway_msg.id]


# Commandes de modération
@bot.command()
async def mute(ctx,
              member: discord.Member,
              time: int = None,
              *,
              reason: str = "Aucune raison spécifiée"):
    """Mute un utilisateur et lui attribue le rôle mute."""
    # Vérifier les permissions avec le nouveau système, en incluant la cible
    if not has_permission(ctx.author, "mute", member):
        await ctx.send("❌ Tu n'as pas la permission de mute cet utilisateur.")
        return

    mute_role = discord.utils.get(ctx.guild.roles, id=MUTE_ROLE_ID)
    if not mute_role:
        await ctx.send("❌ Le rôle mute est introuvable.")
        return

    await member.add_roles(mute_role, reason=reason)
    await ctx.send(f"🔇 {member.mention} a été mute. Raison : {reason}")

    # Log de l'action
    await log_action(ctx, "Mute", member, reason=f"{reason} | Temps: {'Infini' if time is None else f'{time} minutes'}")

    # Si un temps est donné, unmute après expiration
    if time:
        await asyncio.sleep(time * 60)
        if mute_role in member.roles:  # Vérifier si le membre a toujours le rôle mute
            await member.remove_roles(mute_role, reason="Fin du mute")
            await ctx.send(f"🔊 {member.mention} a été unmute.")
            await log_action(ctx, "Unmute automatique", member)

@bot.command()
async def unmute(ctx, member: discord.Member):
    """Unmute un utilisateur et lui retire le rôle mute."""
    # Vérifier les permissions avec le nouveau système, en incluant la cible
    if not has_permission(ctx.author, "unmute", member):
        await ctx.send("❌ Tu n'as pas la permission d'unmute cet utilisateur.")
        return

    mute_role = discord.utils.get(ctx.guild.roles, id=MUTE_ROLE_ID)
    if not mute_role:
        await ctx.send("❌ Le rôle mute est introuvable.")
        return

    if mute_role not in member.roles:
        await ctx.send(f"❌ {member.mention} n'est pas mute.")
        return

    await member.remove_roles(mute_role, reason="Unmute manuel")
    await ctx.send(f"🔊 {member.mention} a été unmute.")
    await log_action(ctx, "Unmute manuel", member)

@bot.command()
async def kick(ctx,
              member: discord.Member,
              *,
              reason: str = "Aucune raison spécifiée"):
    """Expulse un utilisateur du serveur."""
    # Vérifier les permissions avec le nouveau système, en incluant la cible
    if not has_permission(ctx.author, "kick", member):
        await ctx.send("❌ Tu n'as pas la permission d'expulser cet utilisateur.")
        return

    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} a été expulsé. Raison : {reason}")
    await log_action(ctx, "Kick", member, reason=reason)

@bot.command()
async def ban(ctx,
             member: discord.Member,
             *,
             reason: str = "Aucune raison spécifiée"):
    """Bannit un utilisateur du serveur."""
    # Vérifier les permissions avec le nouveau système, en incluant la cible
    if not has_permission(ctx.author, "ban", member):
        await ctx.send("❌ Tu n'as pas la permission de bannir cet utilisateur.")
        return

    await member.ban(reason=reason)
    await ctx.send(f"🚫 {member.mention} a été banni. Raison : {reason}")
    await log_action(ctx, "Ban", member, reason=reason)

@bot.command()
async def unban(ctx,
               member: discord.User,
               *,
               reason: str = "Aucune raison spécifiée"):
    """Débannit un utilisateur du serveur."""
    # Vérifier les permissions avec le nouveau système
    if not has_permission(ctx.author, "unban"):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Vérifier si l'utilisateur est banni
    try:
        ban_entry = await ctx.guild.fetch_ban(member)
    except discord.NotFound:
        await ctx.send(f"❌ {member.name} n'est pas banni.")
        return

    await ctx.guild.unban(member, reason=reason)
    await ctx.send(f"✅ {member.mention} a été débanni. Raison : {reason}")
    await log_action(ctx, "Unban", member, reason=reason)

@bot.command()
async def warn(ctx,
              member: discord.Member,
              *,
              reason: str = "Aucune raison spécifiée"):
    """Ajoute un avertissement à un utilisateur."""
    # Vérifier les permissions avec le nouveau système, en incluant la cible
    if not has_permission(ctx.author, "warn", member):
        await ctx.send("❌ Tu n'as pas la permission d'avertir cet utilisateur.")
        return

    # Initialiser les avertissements si nécessaire
    if member.id not in warnings:
        warnings[member.id] = 0

    warnings[member.id] += 1

    await ctx.send(f"⚠️ {member.mention} a été averti. Raison : {reason}\n"
                   f"Avertissements actuels : {warnings[member.id]}")

    await log_action(ctx, "Avertissement", member,
                   reason=f"{reason} | Total: {warnings[member.id]}")

    # Action en fonction du nombre d'avertissements
    if warnings[member.id] >= 3:
        await member.kick(reason="Nombre d'avertissements trop élevé.")
        await ctx.send(
            f"❌ {member.mention} a été kické pour avoir atteint 3 avertissements."
        )
        await log_action(ctx, "Kick automatique", member,
               reason=f"A atteint {warnings[member.id]} avertissements")
        warnings[member.id] = 0


# Commandes de gestion des rôles
@bot.command()
async def addrole(ctx, member: discord.Member, role: discord.Role):
    """Ajoute un rôle à un utilisateur."""
    # Vérifier les permissions avec le nouveau système, en incluant la cible
    if not has_permission(ctx.author, "addrole", member):
        await ctx.send("❌ Tu n'as pas la permission d'ajouter un rôle à cet utilisateur.")
        return

    if role in member.roles:
        await ctx.send(f'{member.mention} a déjà le rôle {role.name}.')
        return

    try:
        # Vérifier si le rôle du bot est plus haut dans la hiérarchie
        bot_member = ctx.guild.get_member(bot.user.id)
        bot_top_role = bot_member.top_role

        if bot_top_role.position <= role.position:
            await ctx.send(f"⚠️ **Erreur de permission** : Le rôle du bot ({bot_top_role.name}) est plus bas que le rôle à attribuer ({role.name}).")
            return

        await member.add_roles(role)
        await ctx.send(f'✅ Le rôle {role.name} a été ajouté à {member.mention}.')
        await log_action(ctx, "ajouté", member, role)
    except discord.Forbidden:
        await ctx.send(f"⚠️ **Erreur de permission** : Le bot n'a pas la permission d'attribuer le rôle {role.name}. Vérifiez que le bot a la permission 'Gérer les rôles'.")
    except Exception as e:
        await ctx.send(f"⚠️ **Erreur** : Impossible d'attribuer le rôle. Erreur: {str(e)}")

@bot.command()
async def removerole(ctx, member: discord.Member, role: discord.Role):
    """Retire un rôle à un utilisateur."""
    # Vérifier les permissions avec le nouveau système, en incluant la cible
    if not has_permission(ctx.author, "removerole", member):
        await ctx.send("❌ Tu n'as pas la permission de retirer un rôle à cet utilisateur.")
        return

    if not role in member.roles:
        await ctx.send(f'{member.mention} n\'a pas le rôle {role.name}.')
        return

    try:
        # Vérifier si le rôle du bot est plus haut dans la hiérarchie
        bot_member = ctx.guild.get_member(bot.user.id)
        bot_top_role = bot_member.top_role

        if bot_top_role.position <= role.position:
            await ctx.send(f"⚠️ **Erreur de permission** : Le rôle du bot ({bot_top_role.name}) est plus bas que le rôle à retirer ({role.name}).")
            return

        await member.remove_roles(role)
        await ctx.send(f'✅ Le rôle {role.name} a été retiré à {member.mention}.')
        await log_action(ctx, "retiré", member, role)
    except discord.Forbidden:
        await ctx.send(f"⚠️ **Erreur de permission** : Le bot n'a pas la permission de retirer le rôle {role.name}. Vérifiez que le bot a la permission 'Gérer les rôles'.")
    except Exception as e:
        await ctx.send(f"⚠️ **Erreur** : Impossible de retirer le rôle. Erreur: {str(e)}")

# Commandes de gestion des mots interdits
@bot.command()
async def addword(ctx, *, word: str):
    """Ajoute un mot à la liste des mots interdits."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if word.lower() not in MOTS_INTERDITS:
        MOTS_INTERDITS.append(word.lower())
        await ctx.send(f"Le mot `{word}` a été ajouté à la liste des interdictions.")
    else:
        await ctx.send(f"Le mot `{word}` est déjà dans la liste.")

@bot.command()
async def removeword(ctx, *, word: str):
    """Retire un mot de la liste des mots interdits."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if word.lower() in MOTS_INTERDITS:
        MOTS_INTERDITS.remove(word.lower())
        await ctx.send(f"Le mot `{word}` a été retiré de la liste des interdictions.")
    else:
        await ctx.send(f"Le mot `{word}` n'est pas dans la liste.")

@bot.command()
async def listwords(ctx):
    """Affiche la liste des mots interdits."""
    # Vérifier les permissions avec le nouveau système
    if not has_permission(ctx.author, "listwords"):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    await ctx.send(f"Liste des mots interdits: {', '.join(MOTS_INTERDITS)}")

# Commande de diagnostic
@bot.command(name="setjoinleavechannel")
async def set_join_leave_channel(ctx, channel: discord.TextChannel = None):
    """Configure le canal pour les logs d'arrivées et départs.

    Utilisation:
    !setjoinleavechannel - Utilise le canal actuel
    !setjoinleavechannel #canal - Utilise le canal spécifié
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Si aucun canal n'est spécifié, utiliser le canal actuel
    if not channel:
        channel = ctx.channel

    # Mettre à jour l'ID du canal
    global LOG_JOIN_LEAVE_ID
    LOG_JOIN_LEAVE_ID = channel.id

    # Sauvegarder la configuration
    if save_config():
        await ctx.send(f"✅ Le canal pour les logs d'arrivées et départs a été configuré sur {channel.mention}.")
    else:
        await ctx.send(f"✅ Le canal pour les logs d'arrivées et départs a été configuré sur {channel.mention}, mais la sauvegarde de la configuration a échoué.")

    # Envoyer un message de test
    embed = discord.Embed(
        title="✅ Configuration des logs d'arrivées/départs",
        description="Ce canal a été configuré pour recevoir les logs d'arrivées et départs des membres.",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"Configuré par {ctx.author.name}")

    await channel.send(embed=embed)

@bot.command(name="checksetup")
async def check_setup(ctx):
    """Vérifie si le serveur est correctement configuré pour le bot."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    embed = discord.Embed(
        title="📋 Vérification de la configuration",
        color=discord.Color.blue(),
        description=f"Serveur: {ctx.guild.name} (ID: {ctx.guild.id})"
    )

    # Vérifier les canaux de logs
    log_channel = discord.utils.get(ctx.guild.text_channels, id=LOG_CHANNEL_ID)
    log_ticket = discord.utils.get(ctx.guild.text_channels, id=LOG_TICKET_ID)
    log_join_leave = discord.utils.get(ctx.guild.text_channels, id=LOG_JOIN_LEAVE_ID)
    embed.add_field(
        name="📝 Canaux de logs",
        value=f"Canal de logs général (ID: {LOG_CHANNEL_ID}): {'✅' if log_channel else '❌'}\n"
              f"Canal de logs tickets (ID: {LOG_TICKET_ID}): {'✅' if log_ticket else '❌'}\n"
              f"Canal de logs arrivées/départs (ID: {LOG_JOIN_LEAVE_ID}): {'✅' if log_join_leave else '❌'}",
        inline=False
    )

    # Vérifier les rôles
    mute_role = discord.utils.get(ctx.guild.roles, id=MUTE_ROLE_ID)
    owner_role = discord.utils.get(ctx.guild.roles, id=OWNER_ROLE_ID)
    admin_role = discord.utils.get(ctx.guild.roles, id=ADMIN_ROLE_ID)
    mod_role = discord.utils.get(ctx.guild.roles, id=MOD_ROLE_ID)
    helper_role = discord.utils.get(ctx.guild.roles, id=HELPER_ROLE_ID)
    join_role = discord.utils.get(ctx.guild.roles, id=ROLE_JOIN_ID)
    giveaway_role = discord.utils.get(ctx.guild.roles, id=GIVEAWAY_WINNER_ROLE_ID)

    # Rôles de staff
    embed.add_field(
        name="👑 Rôles de staff",
        value=f"Rôle propriétaire (ID: {OWNER_ROLE_ID}): {'✅' if owner_role else '❌'}\n"
              f"Rôle administrateur (ID: {ADMIN_ROLE_ID}): {'✅' if admin_role else '❌'}\n"
              f"Rôle modérateur (ID: {MOD_ROLE_ID}): {'✅' if mod_role else '❌'}\n"
              f"Rôle helper (ID: {HELPER_ROLE_ID}): {'✅' if helper_role else '❌'}\n"
              f"Rôle mute (ID: {MUTE_ROLE_ID}): {'✅' if mute_role else '❌'}",
        inline=False
    )

    # Rôles personnalisés
    if CUSTOM_ROLES:
        custom_roles_text = []
        for role_name, role_data in CUSTOM_ROLES.items():
            role_id = role_data.get("id")
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            status = "✅" if role else "❌"
            cmd_count = len(role_data.get("permissions", []))
            custom_roles_text.append(f"{role_name} (ID: {role_id}): {status} ({cmd_count} commandes)")

        embed.add_field(
            name="🔑 Rôles personnalisés",
            value="\n".join(custom_roles_text),
            inline=False
        )
    else:
        embed.add_field(
            name="🔑 Rôles personnalisés",
            value="Aucun rôle personnalisé configuré",
            inline=False
        )

    # Autres rôles
    embed.add_field(
        name="🏷️ Autres rôles",
        value=f"Rôle join (ID: {ROLE_JOIN_ID}): {'✅' if join_role else '❌'}\n"
              f"Rôle giveaway (ID: {GIVEAWAY_WINNER_ROLE_ID}): {'✅' if giveaway_role else '❌'}",
        inline=False
    )

    # Vérifier les catégories
    categories = ["📌 Candidatures", "❓ Aide", "🚫 Débannissement", "🤝 Partenariats"]
    categories_status = []
    for cat_name in categories:
        category = discord.utils.get(ctx.guild.categories, name=cat_name)
        categories_status.append(f"{cat_name}: {'✅' if category else '❌'}")

    embed.add_field(
        name="📂 Catégories",
        value="\n".join(categories_status),
        inline=False
    )

    # Vérifier le canal de support
    support_channel = discord.utils.get(ctx.guild.text_channels, name="ticket-support")
    embed.add_field(
        name="🎫 Canal de support",
        value=f"ticket-support: {'✅' if support_channel else '❌'}",
        inline=False
    )

    # Vérifier les permissions du bot
    bot_member = ctx.guild.get_member(bot.user.id)
    permissions = []
    required_perms = {
        "manage_channels": "Gérer les canaux",
        "manage_roles": "Gérer les rôles",
        "manage_messages": "Gérer les messages",
        "read_messages": "Lire les messages",
        "send_messages": "Envoyer des messages"
    }

    for perm, name in required_perms.items():
        has_perm = getattr(bot_member.guild_permissions, perm)
        permissions.append(f"{name}: {'✅' if has_perm else '❌'}")

    embed.add_field(
        name="🔑 Permissions du bot",
        value="\n".join(permissions),
        inline=False
    )

    await ctx.send(embed=embed)

# Commande pour recréer le message de ticket
@bot.command(name="resetticket")
async def reset_ticket(ctx):
    """Supprime et recrée le message de ticket dans le canal ticket-support."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    support_channel = discord.utils.get(ctx.guild.text_channels, name="ticket-support")
    if not support_channel:
        await ctx.send("❌ Le canal ticket-support n'existe pas. Crée-le d'abord.")
        return

    # Supprimer les anciens messages du bot
    deleted = 0
    async for message in support_channel.history(limit=100):
        if message.author == bot.user and "Choisis une catégorie pour ton ticket" in message.content:
            await message.delete()
            deleted += 1

    # Créer un nouveau message
    view = TicketView()
    await support_channel.send("📝 **Choisis une catégorie pour ton ticket :**", view=view)

    await ctx.send(f"✅ {deleted} ancien(s) message(s) supprimé(s) et un nouveau message de ticket créé dans {support_channel.mention}")

# Commande pour créer les catégories manquantes
@bot.command(name="setuptickets")
async def setup_tickets(ctx):
    """Crée les catégories et canaux nécessaires pour le système de tickets."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Créer les catégories si elles n'existent pas
    categories = ["📌 Candidatures", "❓ Aide", "🚫 Débannissement", "🤝 Partenariats", "🚨 Plainte Staff"]
    created_categories = []

    for cat_name in categories:
        category = discord.utils.get(ctx.guild.categories, name=cat_name)
        if not category:
            try:
                category = await ctx.guild.create_category(cat_name)
                created_categories.append(cat_name)
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la création de la catégorie {cat_name}: {e}")
                return

    # Créer le canal de support s'il n'existe pas
    support_channel = discord.utils.get(ctx.guild.text_channels, name="ticket-support")
    if not support_channel:
        try:
            support_channel = await ctx.guild.create_text_channel("ticket-support")
            await ctx.send(f"✅ Canal {support_channel.mention} créé.")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la création du canal ticket-support: {e}")
            return

    # Créer le canal de logs s'il n'existe pas
    log_channel = discord.utils.get(ctx.guild.text_channels, id=LOG_TICKET_ID)
    if not log_channel:
        try:
            log_channel = await ctx.guild.create_text_channel("logs-tickets")
            await ctx.send(f"✅ Canal de logs {log_channel.mention} créé. N'oublie pas de mettre à jour la variable LOG_TICKET_ID dans le code avec l'ID: {log_channel.id}")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la création du canal de logs: {e}")

    # Vérifier s'il faut créer un message dans le canal de support
    has_ticket_message = False
    async for message in support_channel.history(limit=100):
        if message.author == bot.user and "Choisis une catégorie pour ton ticket" in message.content:
            has_ticket_message = True
            break

    # Créer un message seulement s'il n'y en a pas déjà un
    if not has_ticket_message:
        view = TicketView()
        await support_channel.send("📝 **Choisis une catégorie pour ton ticket :**", view=view)

    # Message de confirmation
    if created_categories:
        await ctx.send(f"✅ Catégories créées: {', '.join(created_categories)}")
    else:
        await ctx.send("✅ Toutes les catégories existent déjà.")

    await ctx.send("✅ Configuration des tickets terminée.")

# La fonction setup_tickets_duplicate a été supprimée car elle était une duplication
# de la commande setuptickets définie plus haut



# Commandes pour le règlement
@bot.command(name="setupreglement")
async def setup_reglement(ctx, channel: discord.TextChannel = None):
    """Configure le canal où afficher le règlement.

    Utilisation:
    !setupreglement - Utilise le canal actuel
    !setupreglement #canal - Utilise le canal spécifié
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Si aucun canal n'est spécifié, utiliser le canal actuel
    if not channel:
        channel = ctx.channel

    # Mettre à jour le canal de règlement
    reglement["channel_id"] = channel.id

    # Sauvegarder les modifications
    save_reglement()

    await ctx.send(f"✅ Le canal de règlement a été configuré sur {channel.mention}.")

    # Vérifier s'il y a déjà des règles à afficher
    if reglement["rules"]:
        await update_reglement_message(ctx.guild)
    else:
        await ctx.send("ℹ️ Aucune règle n'est définie. Utilise `!addrule <règle>` pour ajouter des règles.")

@bot.command(name="addrule")
async def add_rule(ctx, *, rule_text: str):
    """Ajoute une règle au règlement.

    Utilisation:
    !addrule Respecter les autres membres
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Vérifier si le canal de règlement est configuré
    if not reglement["channel_id"]:
        await ctx.send("❌ Le canal de règlement n'est pas configuré. Utilise d'abord `!setupreglement`.")
        return

    # Ajouter la règle
    reglement["rules"].append(rule_text)

    # Sauvegarder les modifications
    save_reglement()

    await ctx.send(f"✅ Règle ajoutée: {rule_text}")

    # Mettre à jour le message de règlement
    await update_reglement_message(ctx.guild)

@bot.command(name="removerule")
async def remove_rule(ctx, index: int):
    """Supprime une règle du règlement par son numéro.

    Utilisation:
    !removerule 2 - Supprime la règle numéro 2
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Vérifier si l'index est valide
    if index <= 0 or index > len(reglement["rules"]):
        await ctx.send(f"❌ Index invalide. Les règles vont de 1 à {len(reglement['rules'])}.")
        return

    # Supprimer la règle (ajuster l'index car les listes commencent à 0)
    removed_rule = reglement["rules"].pop(index - 1)

    # Sauvegarder les modifications
    save_reglement()

    await ctx.send(f"✅ Règle supprimée: {removed_rule}")

    # Mettre à jour le message de règlement
    await update_reglement_message(ctx.guild)

@bot.command(name="editrule")
async def edit_rule(ctx, index: int, *, new_text: str):
    """Modifie une règle existante par son numéro.

    Utilisation:
    !editrule 2 Nouvelle formulation de la règle
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Vérifier si l'index est valide
    if index <= 0 or index > len(reglement["rules"]):
        await ctx.send(f"❌ Index invalide. Les règles vont de 1 à {len(reglement['rules'])}.")
        return

    # Sauvegarder l'ancienne règle pour l'afficher
    old_rule = reglement["rules"][index - 1]

    # Modifier la règle
    reglement["rules"][index - 1] = new_text

    # Sauvegarder les modifications
    save_reglement()

    await ctx.send(f"✅ Règle modifiée:\nAncienne: {old_rule}\nNouvelle: {new_text}")

    # Mettre à jour le message de règlement
    await update_reglement_message(ctx.guild)

# Classe pour le bouton de vérification par règlement
class ReglementVerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Pas de timeout pour que le bouton reste actif

    @discord.ui.button(label="✅ J'ai lu et j'accepte le règlement",
                      style=discord.ButtonStyle.success,
                      custom_id="reglement_verification_button")
    async def verify_button(self, button, interaction):
        print(f"=== Bouton de vérification règlement cliqué ===")
        print(f"Type du premier paramètre: {type(button)}")
        print(f"Type du deuxième paramètre: {type(interaction)}")

        # Déterminer quel paramètre est l'interaction
        if isinstance(button, discord.Interaction):
            real_interaction = button
            print(f"L'interaction est le premier paramètre")
        elif isinstance(interaction, discord.Interaction):
            real_interaction = interaction
            print(f"L'interaction est le deuxième paramètre")
        else:
            print(f"Aucun paramètre n'est une interaction valide")
            return

        print(f"Utilisateur: {real_interaction.user.name} (ID: {real_interaction.user.id})")

        try:
            # Attribuer le rôle membre (ID spécifique: 1354904148570542273)
            print(f"Recherche du rôle membre (ID: 1354904148570542273) dans le serveur {real_interaction.guild.name}")
            role = discord.utils.get(real_interaction.guild.roles, id=1354904148570542273)

            if not role:
                print(f"❌ Rôle membre introuvable dans le serveur {real_interaction.guild.name}")
                # Afficher tous les rôles disponibles pour le débogage
                available_roles = [f"{r.name} (ID: {r.id})" for r in real_interaction.guild.roles]
                print(f"Rôles disponibles: {', '.join(available_roles)}")

                await real_interaction.response.send_message(
                    "❌ Le rôle membre est introuvable. Contacte un administrateur.",
                    ephemeral=True
                )
                return

            print(f"✅ Rôle membre trouvé: {role.name} (ID: {role.id})")

            # Vérifier la hiérarchie des rôles
            bot_member = real_interaction.guild.get_member(real_interaction.client.user.id)
            if bot_member.top_role.position <= role.position:
                await real_interaction.response.send_message(
                    "❌ Je n'ai pas la permission d'attribuer ce rôle. Contacte un administrateur.",
                    ephemeral=True
                )
                return

            # Attribuer le rôle
            await real_interaction.user.add_roles(role)

            # Confirmer à l'utilisateur
            await real_interaction.response.send_message(
                f"✅ Merci d'avoir accepté le règlement ! Tu as maintenant accès au serveur.",
                ephemeral=True
            )

            # Log de l'action
            log_channel = real_interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(
                    f"✅ **Vérification par règlement** : {real_interaction.user.mention} a accepté le règlement et a reçu le rôle {role.mention}."
                )

        except discord.Forbidden:
            await real_interaction.response.send_message(
                "❌ Je n'ai pas la permission d'attribuer ce rôle. Contacte un administrateur.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Erreur lors de la vérification par règlement: {e}")
            await real_interaction.response.send_message(
                "❌ Une erreur s'est produite. Contacte un administrateur.",
                ephemeral=True
            )

@bot.command(name="showrules")
async def show_rules(ctx):
    """Affiche la liste des règles avec leurs numéros et un bouton pour accepter le règlement."""
    # Cette commande peut être utilisée par tout le monde

    if not reglement["rules"]:
        await ctx.send("ℹ️ Aucune règle n'est définie.")
        return

    # Créer un embed pour afficher les règles
    embed = discord.Embed(
        title="📜 Règlement du serveur",
        description="Voici les règles à respecter sur ce serveur:",
        color=discord.Color.blue()
    )

    # Ajouter une image de bannière en haut de l'embed
    if "banner_url" in reglement and reglement["banner_url"]:
        embed.set_image(url=reglement["banner_url"])
    else:
        # Utiliser une bannière par défaut si aucune n'est définie
        embed.set_image(url="https://i.imgur.com/tJtAdNs.png")

    # Ajouter l'icône du serveur comme thumbnail
    try:
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'icône du serveur: {e}")
        pass

    # Formater les règles avec des séparateurs
    rules_text = format_rules_with_separators(reglement["rules"])

    # Si la description est trop longue pour un seul embed (limite de 4096 caractères)
    if len(rules_text) <= 4096:
        embed.description = f"Voici les règles à respecter sur ce serveur:\n\n{rules_text}"
    else:
        # Diviser les règles en plusieurs embeds si nécessaire
        embed.description = "Voici les règles à respecter sur ce serveur:"

        # Utiliser la fonction utilitaire pour ajouter les règles aux champs
        add_rules_to_embed_fields(embed, reglement["rules"])

    # Ajouter un pied de page
    embed.set_footer(text=f"Règlement demandé par {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    # Créer la vue avec le bouton de vérification
    verification_view = ReglementVerificationView()

    # Envoyer l'embed avec le bouton
    await ctx.send(embed=embed, view=verification_view)

@bot.command(name="setbanner")
async def set_banner(ctx, url: str = None):
    """Change la bannière du règlement.

    Utilisation:
    !setbanner https://exemple.com/image.png - Définit une nouvelle bannière
    !setbanner - Affiche la bannière actuelle
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Si aucune URL n'est fournie, afficher la bannière actuelle
    if not url:
        banner_url = reglement.get("banner_url", "https://i.imgur.com/tJtAdNs.png")
        embed = discord.Embed(
            title="Bannière actuelle du règlement",
            description=f"URL: {banner_url}",
            color=discord.Color.blue()
        )
        embed.set_image(url=banner_url)
        await ctx.send(embed=embed)
        return

    # Vérifier si l'URL semble valide
    if not (url.startswith("http://") or url.startswith("https://")) or not any(url.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]):
        await ctx.send("❌ L'URL doit commencer par http:// ou https:// et se terminer par une extension d'image (.png, .jpg, .jpeg, .gif, .webp).")
        return

    # Sauvegarder l'ancienne URL
    old_url = reglement["banner_url"]

    # Mettre à jour l'URL de la bannière
    reglement["banner_url"] = url

    # Sauvegarder les modifications
    save_reglement()

    # Confirmer le changement
    embed = discord.Embed(
        title="✅ Bannière du règlement mise à jour",
        description="La nouvelle bannière sera utilisée pour tous les affichages du règlement.",
        color=discord.Color.green()
    )
    embed.set_image(url=url)
    await ctx.send(embed=embed)

    # Mettre à jour le message de règlement
    if reglement["channel_id"] and reglement["rules"]:
        await update_reglement_message(ctx.guild)

@bot.command(name="resetrules")
async def reset_rules(ctx):
    """Supprime toutes les règles du règlement."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Demander confirmation
    confirmation_message = await ctx.send("⚠️ Êtes-vous sûr de vouloir supprimer toutes les règles ? Répondez par 'oui' pour confirmer.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["oui", "non", "yes", "no"]

    try:
        # Attendre la réponse pendant 30 secondes
        response = await bot.wait_for('message', check=check, timeout=30.0)

        if response.content.lower() in ["oui", "yes"]:
            # Supprimer toutes les règles
            reglement["rules"] = []

            # Sauvegarder les modifications
            save_reglement()

            await ctx.send("✅ Toutes les règles ont été supprimées.")

            # Mettre à jour le message de règlement (le supprimer s'il existe)
            if reglement["message_id"] and reglement["channel_id"]:
                channel = ctx.guild.get_channel(reglement["channel_id"])
                if channel:
                    try:
                        message = await channel.fetch_message(reglement["message_id"])
                        await message.delete()
                        reglement["message_id"] = None
                        save_reglement()
                    except:
                        pass
        else:
            await ctx.send("❌ Opération annulée.")

    except asyncio.TimeoutError:
        await ctx.send("❌ Temps écoulé. Opération annulée.")

# Fonction pour mettre à jour le message de règlement
async def update_reglement_message(guild):
    # Vérifier si le canal est configuré
    if not reglement["channel_id"]:
        return False

    # Récupérer le canal
    channel = guild.get_channel(reglement["channel_id"])
    if not channel:
        print(f"Canal de règlement introuvable (ID: {reglement['channel_id']})")
        return False

    # Créer l'embed pour le règlement
    embed = discord.Embed(
        title="📜 Règlement du serveur",
        description="Voici les règles à respecter sur ce serveur:",
        color=discord.Color.blue()
    )

    # Ajouter une image de bannière en haut de l'embed
    if "banner_url" in reglement and reglement["banner_url"]:
        embed.set_image(url=reglement["banner_url"])
    else:
        # Utiliser une bannière par défaut si aucune n'est définie
        embed.set_image(url="https://i.imgur.com/tJtAdNs.png")

    # Ajouter l'icône du serveur comme thumbnail
    try:
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'icône du serveur: {e}")
        pass

    # Formater les règles avec des séparateurs
    rules_text = format_rules_with_separators(reglement["rules"])

    # Si la description est trop longue pour un seul embed (limite de 4096 caractères)
    if len(rules_text) <= 4096:
        embed.description = f"Voici les règles à respecter sur ce serveur:\n\n{rules_text}"
    else:
        # Diviser les règles en plusieurs embeds si nécessaire
        embed.description = "Voici les règles à respecter sur ce serveur:"

        # Utiliser la fonction utilitaire pour ajouter les règles aux champs
        add_rules_to_embed_fields(embed, reglement["rules"])

    # Ajouter un pied de page
    embed.set_footer(text=f"Dernière mise à jour: {discord.utils.utcnow().strftime('%d/%m/%Y %H:%M')}")

    try:
        # Créer la vue avec le bouton de vérification
        verification_view = ReglementVerificationView()

        # Si un message existe déjà, le mettre à jour
        if reglement["message_id"]:
            try:
                message = await channel.fetch_message(reglement["message_id"])
                await message.edit(embed=embed, view=verification_view)
                return True
            except discord.NotFound:
                # Le message n'existe plus, en créer un nouveau
                reglement["message_id"] = None

        # Créer un nouveau message
        message = await channel.send(embed=embed, view=verification_view)
        reglement["message_id"] = message.id
        save_reglement()
        return True

    except Exception as e:
        print(f"Erreur lors de la mise à jour du message de règlement: {e}")
        return False

# Fonction utilitaire pour formater les règles avec des séparateurs
def format_rules_with_separators(rules):
    rules_text = ""
    separator = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    for i, rule in enumerate(rules, 1):
        # Ajouter un séparateur avant chaque règle (sauf la première)
        if i > 1:
            rules_text += f"\n\n{separator}\n\n"

        # Ajouter la règle avec son numéro
        rules_text += f"**Règle {i}**\n{rule}"

    # Ajouter un séparateur final
    rules_text += f"\n\n{separator}"

    return rules_text

# Fonction utilitaire pour diviser les règles en champs d'embed
def add_rules_to_embed_fields(embed, rules):
    separator = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    current_field = ""
    field_count = 1

    for i, rule in enumerate(rules, 1):
        # Créer le texte de la règle avec séparateur
        if i > 1:
            rule_prefix = f"\n{separator}\n\n**Règle {i}**\n"
        else:
            rule_prefix = f"**Règle {i}**\n"

        rule_text = f"{rule_prefix}{rule}\n\n"

        # Si l'ajout de cette règle dépasse la limite de caractères d'un champ (1024)
        if len(current_field) + len(rule_text) > 1024:
            # Ajouter le champ actuel à l'embed
            embed.add_field(name=f"Partie {field_count}", value=current_field, inline=False)
            # Commencer un nouveau champ
            current_field = rule_text
            field_count += 1
        else:
            # Ajouter la règle au champ actuel
            current_field += rule_text

    # Ajouter un séparateur final au dernier champ
    if current_field and not current_field.endswith(f"{separator}\n\n"):
        current_field += f"{separator}"

    # Ajouter le dernier champ s'il n'est pas vide
    if current_field:
        embed.add_field(name=f"Partie {field_count}", value=current_field, inline=False)

# Fonction pour mettre à jour le message de règlement au démarrage
async def update_reglement_on_startup():
    # Charger le règlement depuis le fichier
    load_reglement()

    # Mettre à jour le message de règlement si nécessaire
    if reglement["channel_id"] and reglement["rules"]:
        for guild in bot.guilds:
            await update_reglement_message(guild)

# Événements pour les logs supplémentaires

# Log des entrées/sorties dans les canaux vocaux
@bot.event
async def on_voice_state_update(member, before, after):
    # Ignorer les bots
    if member.bot:
        return

    # Récupérer le canal de logs
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return

    # Création d'un embed pour le log
    embed = discord.Embed(
        title="🔊 Activité Vocale",
        color=0x3498db,
        timestamp=datetime.datetime.now()
    )
    embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar.url if member.avatar else None)
    embed.set_footer(text=f"ID Utilisateur: {member.id}")

    # Cas 1: L'utilisateur a rejoint un canal vocal
    if before.channel is None and after.channel is not None:
        embed.description = f"**{member.mention} a rejoint le canal vocal {after.channel.mention}**"
        embed.color = 0x2ecc71  # Vert

    # Cas 2: L'utilisateur a quitté un canal vocal
    elif before.channel is not None and after.channel is None:
        embed.description = f"**{member.mention} a quitté le canal vocal {before.channel.mention}**"
        embed.color = 0xe74c3c  # Rouge

    # Cas 3: L'utilisateur a changé de canal vocal
    elif before.channel != after.channel:
        embed.description = f"**{member.mention} a changé de canal vocal**\n📤 De: {before.channel.mention}\n📥 À: {after.channel.mention}"
        embed.color = 0xf1c40f  # Jaune

    # Cas 4: L'utilisateur a modifié son état dans le même canal (muet, sourdine, etc.)
    else:
        changes = []

        # Vérifier les changements d'état
        if before.deaf != after.deaf:
            changes.append(f"**Sourdine serveur**: {'Activée ✅' if after.deaf else 'Désactivée ❌'}")

        if before.mute != after.mute:
            changes.append(f"**Muet serveur**: {'Activé ✅' if after.mute else 'Désactivé ❌'}")

        if before.self_deaf != after.self_deaf:
            changes.append(f"**Sourdine personnelle**: {'Activée ✅' if after.self_deaf else 'Désactivée ❌'}")

        if before.self_mute != after.self_mute:
            changes.append(f"**Muet personnel**: {'Activé ✅' if after.self_mute else 'Désactivé ❌'}")

        if before.self_stream != after.self_stream:
            changes.append(f"**Partage d'écran**: {'Démarré ✅' if after.self_stream else 'Arrêté ❌'}")

        if before.self_video != after.self_video:
            changes.append(f"**Caméra**: {'Activée ✅' if after.self_video else 'Désactivée ❌'}")

        # S'il y a des changements, les afficher
        if changes:
            embed.description = f"**{member.mention} a modifié son état dans {after.channel.mention}**"
            embed.add_field(name="Changements", value="\n".join(changes), inline=False)
            embed.color = 0x9b59b6  # Violet
        else:
            # Aucun changement significatif, ne pas envoyer de log
            return

    # Envoyer l'embed dans le canal de logs
    await log_channel.send(embed=embed)

# Log des modifications de rôles des utilisateurs
@bot.event
async def on_member_update(before, after):
    # Ignorer les bots
    if before.bot:
        return

    # Récupérer le canal de logs
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return

    # Vérifier si les rôles ont changé
    if before.roles != after.roles:
        # Créer un embed pour le log
        embed = discord.Embed(
            title="👤 Modification de Rôles",
            description=f"Les rôles de {after.mention} ont été modifiés",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=f"{after.name}#{after.discriminator}", icon_url=after.avatar.url if after.avatar else None)
        embed.set_footer(text=f"ID Utilisateur: {after.id}")

        # Trouver les rôles ajoutés
        roles_added = [role for role in after.roles if role not in before.roles]
        if roles_added:
            embed.add_field(
                name="✅ Rôles Ajoutés",
                value="\n".join([f"{role.mention} (`{role.id}`)" for role in roles_added]),
                inline=False
            )

        # Trouver les rôles retirés
        roles_removed = [role for role in before.roles if role not in after.roles]
        if roles_removed:
            embed.add_field(
                name="❌ Rôles Retirés",
                value="\n".join([f"{role.mention} (`{role.id}`)" for role in roles_removed]),
                inline=False
            )

        # Envoyer l'embed dans le canal de logs
        await log_channel.send(embed=embed)

    # Vérifier si le surnom a changé
    if before.nick != after.nick:
        embed = discord.Embed(
            title="👤 Modification de Surnom",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=f"{after.name}#{after.discriminator}", icon_url=after.avatar.url if after.avatar else None)
        embed.set_footer(text=f"ID Utilisateur: {after.id}")

        # Afficher l'ancien et le nouveau surnom
        embed.add_field(name="Ancien surnom", value=before.nick or "*Aucun surnom*", inline=True)
        embed.add_field(name="Nouveau surnom", value=after.nick or "*Aucun surnom*", inline=True)

        # Envoyer l'embed dans le canal de logs
        await log_channel.send(embed=embed)

# Log des changements sur le serveur
@bot.event
async def on_guild_update(before, after):
    # Récupérer le canal de logs
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return

    changes = []

    # Vérifier les changements du serveur
    if before.name != after.name:
        changes.append(f"**Nom du serveur**: `{before.name}` → `{after.name}`")

    if before.description != after.description:
        changes.append(f"**Description**: `{before.description or 'Aucune'}` → `{after.description or 'Aucune'}`")

    if before.region != after.region:
        changes.append(f"**Région**: `{before.region}` → `{after.region}`")

    if before.owner_id != after.owner_id:
        changes.append(f"**Propriétaire**: <@{before.owner_id}> → <@{after.owner_id}>")

    if before.afk_timeout != after.afk_timeout:
        changes.append(f"**Délai AFK**: `{before.afk_timeout} secondes` → `{after.afk_timeout} secondes`")

    if before.afk_channel != after.afk_channel:
        before_afk = before.afk_channel.mention if before.afk_channel else "Aucun"
        after_afk = after.afk_channel.mention if after.afk_channel else "Aucun"
        changes.append(f"**Canal AFK**: {before_afk} → {after_afk}")

    if before.verification_level != after.verification_level:
        changes.append(f"**Niveau de vérification**: `{before.verification_level}` → `{after.verification_level}`")

    if before.explicit_content_filter != after.explicit_content_filter:
        changes.append(f"**Filtre de contenu explicite**: `{before.explicit_content_filter}` → `{after.explicit_content_filter}`")

    if before.default_notifications != after.default_notifications:
        changes.append(f"**Notifications par défaut**: `{before.default_notifications}` → `{after.default_notifications}`")

    if before.system_channel != after.system_channel:
        before_system = before.system_channel.mention if before.system_channel else "Aucun"
        after_system = after.system_channel.mention if after.system_channel else "Aucun"
        changes.append(f"**Canal système**: {before_system} → {after_system}")

    if before.premium_tier != after.premium_tier:
        changes.append(f"**Niveau de boost**: `{before.premium_tier}` → `{after.premium_tier}`")

    if before.premium_subscription_count != after.premium_subscription_count:
        changes.append(f"**Nombre de boosts**: `{before.premium_subscription_count}` → `{after.premium_subscription_count}`")

    # Si des changements ont été détectés, créer et envoyer un embed
    if changes:
        embed = discord.Embed(
            title="🔧 Modification du Serveur",
            description="\n".join(changes),
            color=0xf1c40f,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=after.name, icon_url=after.icon.url if after.icon else None)
        embed.set_footer(text=f"ID Serveur: {after.id}")

        # Envoyer l'embed dans le canal de logs
        await log_channel.send(embed=embed)

# Commandes pour configurer les rôles de staff
@bot.command(name="setownerrole")
async def set_owner_role(ctx, role: discord.Role = None):
    """Définit le rôle de propriétaire du serveur."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if role is None:
        await ctx.send("❌ Usage: `!setownerrole @role`")
        return

    global OWNER_ROLE_ID
    OWNER_ROLE_ID = role.id
    save_config()

    await ctx.send(f"✅ Le rôle de propriétaire a été défini sur {role.mention} (ID: {role.id}).")

@bot.command(name="setadminrole")
async def set_admin_role(ctx, role: discord.Role = None):
    """Définit le rôle d'administrateur."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if role is None:
        await ctx.send("❌ Usage: `!setadminrole @role`")
        return

    global ADMIN_ROLE_ID
    ADMIN_ROLE_ID = role.id
    save_config()

    await ctx.send(f"✅ Le rôle d'administrateur a été défini sur {role.mention} (ID: {role.id}).")

@bot.command(name="setmodrole")
async def set_mod_role(ctx, role: discord.Role = None):
    """Définit le rôle de modérateur."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if role is None:
        await ctx.send("❌ Usage: `!setmodrole @role`")
        return

    global MOD_ROLE_ID
    MOD_ROLE_ID = role.id
    save_config()

    await ctx.send(f"✅ Le rôle de modérateur a été défini sur {role.mention} (ID: {role.id}).")

@bot.command(name="sethelperrole")
async def set_helper_role(ctx, role: discord.Role = None):
    """Définit le rôle de helper."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if role is None:
        await ctx.send("❌ Usage: `!sethelperrole @role`")
        return

    global HELPER_ROLE_ID
    HELPER_ROLE_ID = role.id
    save_config()

    await ctx.send(f"✅ Le rôle de helper a été défini sur {role.mention} (ID: {role.id}).")

@bot.command(name="createrole")
async def create_custom_role(ctx, role_name: str = None, color: str = None, *commands):
    """
    Crée un nouveau rôle Discord et lui attribue des permissions spécifiques.

    Usage:
    !createrole <nom_du_role> <couleur_hex> commande1 commande2 commande3 ...

    Exemple:
    !createrole Support #FF0000 kick mute warn clear
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if role_name is None:
        await ctx.send("❌ Usage: `!createrole <nom_du_role> <couleur_hex> commande1 commande2 ...`\n"
                      "Exemple: `!createrole Support #FF0000 kick mute warn clear`")
        return

    # Vérifier si un rôle avec ce nom existe déjà
    existing_role = discord.utils.get(ctx.guild.roles, name=role_name)
    if existing_role:
        await ctx.send(f"⚠️ Un rôle nommé **{role_name}** existe déjà. Veuillez choisir un autre nom ou utiliser `!setrole` pour configurer ce rôle existant.")
        return

    # Convertir la couleur hexadécimale en couleur Discord
    role_color = discord.Color.default()
    if color:
        try:
            # Supprimer le # si présent
            if color.startswith('#'):
                color = color[1:]
            # Convertir la couleur hex en int
            color_int = int(color, 16)
            role_color = discord.Color(color_int)
        except ValueError:
            await ctx.send(f"⚠️ Couleur invalide. Utilisation de la couleur par défaut.")

    # Créer le nouveau rôle
    try:
        new_role = await ctx.guild.create_role(
            name=role_name,
            color=role_color,
            reason=f"Rôle créé par {ctx.author.name} via la commande !createrole"
        )

        # Convertir les commandes en liste
        commands_list = list(commands)
        if not commands_list:
            await ctx.send("⚠️ Aucune commande spécifiée. Ce rôle n'aura aucune permission.")

        # Ajouter le rôle personnalisé
        global CUSTOM_ROLES
        CUSTOM_ROLES[role_name] = {
            "id": new_role.id,
            "permissions": commands_list
        }

        # Sauvegarder la configuration
        save_config()

        # Créer un message de confirmation avec la liste des commandes
        commands_str = ", ".join([f"`!{cmd}`" for cmd in commands_list]) if commands_list else "Aucune"

        await ctx.send(f"✅ Le rôle **{role_name}** a été créé avec succès {new_role.mention} (ID: {new_role.id}).\n"
                      f"**Commandes autorisées**: {commands_str}")

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de créer des rôles sur ce serveur.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur s'est produite lors de la création du rôle: {str(e)}")

@bot.command(name="setrole")
async def set_custom_role(ctx, role_name: str = None, role_input = None, *commands):
    """
    Définit un rôle personnalisé avec des permissions spécifiques.

    Usage:
    !setrole <nom_du_role> <@role ou nom du rôle> commande1 commande2 commande3 ...

    Exemples:
    !setrole support @Support kick mute warn clear
    !setrole events "Event Team" giveaway clear
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if role_name is None or role_input is None:
        await ctx.send("❌ Usage: `!setrole <nom_du_role> <@role ou nom du rôle> commande1 commande2 ...`\n"
                      "Exemples:\n"
                      "`!setrole support @Support kick mute warn clear`\n"
                      "`!setrole events \"Event Team\" giveaway clear`")
        return

    # Trouver le rôle Discord
    role = None

    # Vérifier si c'est une mention de rôle
    if ctx.message.role_mentions:
        role = ctx.message.role_mentions[0]
    else:
        # Chercher le rôle par nom
        role = discord.utils.get(ctx.guild.roles, name=role_input)

        # Si le rôle n'est pas trouvé, essayer de chercher de manière insensible à la casse
        if not role:
            for guild_role in ctx.guild.roles:
                if guild_role.name.lower() == role_input.lower():
                    role = guild_role
                    break

    # Si le rôle n'est pas trouvé
    if not role:
        await ctx.send(f"❌ Le rôle **{role_input}** n'a pas été trouvé sur le serveur.")
        return

    # Vérifier si c'est un rôle protégé
    if role.id == OWNER_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle propriétaire (owner). Vous pouvez le configurer, mais cela n'affectera pas ses permissions spéciales.")

    if role.id == ADMIN_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle administrateur (admin). Vous pouvez le configurer, mais cela n'affectera pas ses permissions spéciales.")

    if role.id == MOD_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle modérateur (mod). Utilisez `!addperm mod` pour modifier ses permissions.")
        return

    if role.id == HELPER_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle helper. Utilisez `!addperm helper` pour modifier ses permissions.")
        return

    # Vérifier si c'est un rôle par défaut (@everyone)
    if role.is_default():
        await ctx.send("⛔ Le rôle @everyone ne peut pas être configuré comme rôle personnalisé.")
        return

    # Vérifier si c'est un rôle intégré (bot)
    if role.is_integration() or role.is_bot_managed():
        await ctx.send("⚠️ Ce rôle est géré par une intégration ou un bot. Vous pouvez le configurer, mais il pourrait être modifié par l'intégration ou le bot.")

    # Convertir les commandes en liste et supprimer le préfixe ! si présent
    commands_list = []
    for cmd in commands:
        if cmd.startswith('!'):
            commands_list.append(cmd[1:])
        else:
            commands_list.append(cmd)

    if not commands_list:
        await ctx.send("⚠️ Aucune commande spécifiée. Ce rôle n'aura aucune permission.")

    # Convertir le nom du rôle en minuscules pour la configuration
    role_name = role_name.lower()

    # Ajouter ou mettre à jour le rôle personnalisé
    global CUSTOM_ROLES
    CUSTOM_ROLES[role_name] = {
        "id": role.id,
        "permissions": commands_list
    }

    # Sauvegarder la configuration
    save_config()

    # Créer un message de confirmation avec la liste des commandes
    commands_str = ", ".join([f"`!{cmd}`" for cmd in commands_list]) if commands_list else "Aucune"

    await ctx.send(f"✅ Le rôle personnalisé **{role_name}** a été configuré avec le rôle {role.mention} (ID: {role.id}).\n"
                  f"**Commandes autorisées**: {commands_str}")

@bot.command(name="listroles")
async def list_custom_roles(ctx):
    """Affiche la liste des rôles personnalisés configurés."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    embed = discord.Embed(
        title="🔑 Rôles personnalisés",
        description="Liste des rôles personnalisés configurés sur ce serveur",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )

    # Ajouter les rôles standard
    standard_roles = [
        ("👑 Propriétaire", OWNER_ROLE_ID, "Accès complet à toutes les commandes"),
        ("🔱 Administrateur", ADMIN_ROLE_ID, "Accès complet à toutes les commandes"),
        ("🔰 Modérateur", MOD_ROLE_ID, ", ".join([f"`!{cmd}`" for cmd in role_permissions["mod"]["commands"]])),
        ("🔹 Helper", HELPER_ROLE_ID, ", ".join([f"`!{cmd}`" for cmd in role_permissions["helper"]["commands"]]))
    ]

    for name, role_id, perms in standard_roles:
        role = discord.utils.get(ctx.guild.roles, id=role_id)
        role_mention = role.mention if role else f"Non configuré (ID: {role_id})"
        embed.add_field(
            name=name,
            value=f"**Rôle**: {role_mention}\n**Permissions**: {perms}",
            inline=False
        )

    # Ajouter les rôles personnalisés
    if CUSTOM_ROLES:
        for role_name, role_data in CUSTOM_ROLES.items():
            role_id = role_data.get("id")
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            role_mention = role.mention if role else f"Non trouvé (ID: {role_id})"

            commands_list = role_data.get("permissions", [])
            commands_str = ", ".join([f"`!{cmd}`" for cmd in commands_list]) if commands_list else "Aucune"

            embed.add_field(
                name=f"🔸 {role_name}",
                value=f"**Rôle**: {role_mention}\n**Commandes**: {commands_str}",
                inline=False
            )
    else:
        embed.add_field(
            name="Aucun rôle personnalisé",
            value="Utilisez `!setrole <nom_du_role> @role commande1 commande2 ...` pour configurer un rôle personnalisé",
            inline=False
        )

    embed.set_footer(text=f"Demandé par {ctx.author.name}")

    await ctx.send(embed=embed)

@bot.command(name="delrole")
async def delete_custom_role(ctx, *, role_input: str = None):
    """
    Supprime un rôle du serveur Discord.

    Cette commande supprime définitivement le rôle du serveur Discord.
    Elle ne peut pas être utilisée sur les rôles owner ou admin.

    Usage:
    !delrole <nom_du_role ou @mention>
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if role_input is None:
        await ctx.send("❌ Usage: `!delrole <nom_du_role ou @mention>`")
        return

    # Essayer de trouver le rôle par mention ou par nom
    role = None

    # Vérifier si c'est une mention de rôle
    if ctx.message.role_mentions:
        role = ctx.message.role_mentions[0]
    else:
        # Chercher le rôle par nom
        role = discord.utils.get(ctx.guild.roles, name=role_input)

        # Si le rôle n'est pas trouvé, essayer de chercher de manière insensible à la casse
        if not role:
            for guild_role in ctx.guild.roles:
                if guild_role.name.lower() == role_input.lower():
                    role = guild_role
                    break

    # Si le rôle n'est toujours pas trouvé, vérifier dans la configuration
    role_name_lower = role_input.lower()
    if not role and role_name_lower in CUSTOM_ROLES:
        role_id = CUSTOM_ROLES[role_name_lower]["id"]
        role = discord.utils.get(ctx.guild.roles, id=role_id)

    # Si le rôle n'est pas trouvé du tout
    if not role:
        await ctx.send(f"❌ Le rôle **{role_input}** n'a pas été trouvé sur le serveur.")
        return

    # Vérifier si c'est un rôle protégé
    if role.id == OWNER_ROLE_ID:
        await ctx.send("⛔ Ce rôle est configuré comme rôle propriétaire (owner) et ne peut pas être supprimé.")
        return

    if role.id == ADMIN_ROLE_ID:
        await ctx.send("⛔ Ce rôle est configuré comme rôle administrateur (admin) et ne peut pas être supprimé.")
        return

    if role.id == MOD_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle modérateur (mod) et ne peut pas être supprimé avec cette commande. Utilisez `!setmodrole` pour le reconfigurer.")
        return

    if role.id == HELPER_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle helper et ne peut pas être supprimé avec cette commande. Utilisez `!sethelperrole` pour le reconfigurer.")
        return

    # Vérifier si c'est un rôle par défaut (@everyone)
    if role.is_default():
        await ctx.send("⛔ Le rôle @everyone ne peut pas être supprimé.")
        return

    # Vérifier si c'est un rôle intégré (bot)
    if role.is_integration() or role.is_bot_managed():
        await ctx.send("⛔ Ce rôle est géré par une intégration ou un bot et ne peut pas être supprimé manuellement.")
        return

    # Vérifier si le rôle est plus haut que celui du bot
    if role.position >= ctx.guild.me.top_role.position:
        await ctx.send("❌ Je ne peux pas supprimer ce rôle car il est plus haut que mon rôle le plus élevé dans la hiérarchie.")
        return

    # Stocker le nom du rôle pour les messages
    role_name = role.name

    # Tenter de supprimer le rôle du serveur
    try:
        await role.delete(reason=f"Supprimé par {ctx.author.name} via la commande !delrole")
        await ctx.send(f"✅ Le rôle Discord **{role_name}** a été supprimé du serveur.")

        # Supprimer également de la configuration si présent
        for custom_role_name, data in list(CUSTOM_ROLES.items()):
            if data["id"] == role.id:
                del CUSTOM_ROLES[custom_role_name]
                save_config()
                await ctx.send(f"✅ Le rôle personnalisé **{custom_role_name}** a également été supprimé de la configuration.")
                break

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de supprimer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Une erreur s'est produite lors de la suppression du rôle: {str(e)}")

@bot.command(name="addrolecommand")
async def add_role_command(ctx, role_input: str = None, *commands):
    """
    Ajoute des commandes à un rôle existant.

    Usage:
    !addrolecommand <nom_du_role ou @mention> commande1 commande2 ...

    Exemples:
    !addrolecommand support kick mute warn
    !addrolecommand @Support ban clear
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if role_input is None or not commands:
        await ctx.send("❌ Usage: `!addrolecommand <nom_du_role ou @mention> commande1 commande2 ...`\n"
                      "Exemples:\n"
                      "`!addrolecommand support kick mute warn`\n"
                      "`!addrolecommand @Support ban clear`")
        return

    # Trouver le rôle Discord et le nom dans la configuration
    role = None
    role_name = None

    # Vérifier si c'est une mention de rôle
    if ctx.message.role_mentions:
        role = ctx.message.role_mentions[0]

        # Chercher le nom du rôle dans la configuration
        for custom_name, data in CUSTOM_ROLES.items():
            if data["id"] == role.id:
                role_name = custom_name
                break

        # Si le rôle n'est pas dans la configuration, utiliser son nom comme identifiant
        if not role_name:
            role_name = role.name.lower()
    else:
        # Chercher d'abord dans la configuration
        role_input_lower = role_input.lower()
        if role_input_lower in CUSTOM_ROLES:
            role_name = role_input_lower
            role_id = CUSTOM_ROLES[role_name]["id"]
            role = discord.utils.get(ctx.guild.roles, id=role_id)
        else:
            # Chercher le rôle par nom
            role = discord.utils.get(ctx.guild.roles, name=role_input)

            # Si le rôle n'est pas trouvé, essayer de chercher de manière insensible à la casse
            if not role:
                for guild_role in ctx.guild.roles:
                    if guild_role.name.lower() == role_input.lower():
                        role = guild_role
                        break

            if role:
                # Chercher si ce rôle est déjà dans la configuration
                for custom_name, data in CUSTOM_ROLES.items():
                    if data["id"] == role.id:
                        role_name = custom_name
                        break

                # Si le rôle n'est pas dans la configuration, utiliser son nom comme identifiant
                if not role_name:
                    role_name = role.name.lower()

    # Si le rôle n'est pas trouvé
    if not role:
        await ctx.send(f"❌ Le rôle **{role_input}** n'a pas été trouvé sur le serveur.")
        return

    # Vérifier si c'est un rôle protégé
    if role.id == MOD_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle modérateur (mod). Utilisez `!addperm mod` pour modifier ses permissions.")
        return

    if role.id == HELPER_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle helper. Utilisez `!addperm helper` pour modifier ses permissions.")
        return

    # Vérifier si c'est un rôle par défaut (@everyone)
    if role.is_default():
        await ctx.send("⛔ Le rôle @everyone ne peut pas être configuré comme rôle personnalisé.")
        return

    # Si le rôle n'est pas dans la configuration, l'ajouter
    if role_name not in CUSTOM_ROLES:
        CUSTOM_ROLES[role_name] = {
            "id": role.id,
            "permissions": []
        }
        await ctx.send(f"✅ Le rôle **{role.name}** a été ajouté à la configuration sous le nom **{role_name}**.")

    # Ajouter les nouvelles commandes
    added_commands = []
    for cmd in commands:
        # Supprimer le préfixe ! si présent
        if cmd.startswith("!"):
            cmd = cmd[1:]

        # Ajouter la commande si elle n'existe pas déjà
        if cmd not in CUSTOM_ROLES[role_name]["permissions"]:
            CUSTOM_ROLES[role_name]["permissions"].append(cmd)
            added_commands.append(cmd)

    # Sauvegarder la configuration
    save_config()

    if added_commands:
        commands_str = ", ".join([f"`!{cmd}`" for cmd in added_commands])
        await ctx.send(f"✅ {len(added_commands)} commande(s) ajoutée(s) au rôle **{role.name}** ({role_name}): {commands_str}")
    else:
        await ctx.send(f"ℹ️ Aucune nouvelle commande ajoutée. Toutes les commandes spécifiées étaient déjà attribuées au rôle **{role.name}** ({role_name}).")

    # Afficher les commandes actuelles
    current_commands = ", ".join([f"`!{cmd}`" for cmd in CUSTOM_ROLES[role_name]["permissions"]]) if CUSTOM_ROLES[role_name]["permissions"] else "Aucune"
    await ctx.send(f"📋 Commandes actuelles pour **{role.name}** ({role_name}): {current_commands}")

@bot.command(name="removerolecommand")
async def remove_role_command(ctx, role_input: str = None, *commands):
    """
    Retire des commandes d'un rôle existant.

    Usage:
    !removerolecommand <nom_du_role ou @mention> commande1 commande2 ...

    Exemples:
    !removerolecommand support kick mute
    !removerolecommand @Support ban
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if role_input is None or not commands:
        await ctx.send("❌ Usage: `!removerolecommand <nom_du_role ou @mention> commande1 commande2 ...`\n"
                      "Exemples:\n"
                      "`!removerolecommand support kick mute`\n"
                      "`!removerolecommand @Support ban`")
        return

    # Trouver le rôle Discord et le nom dans la configuration
    role = None
    role_name = None

    # Vérifier si c'est une mention de rôle
    if ctx.message.role_mentions:
        role = ctx.message.role_mentions[0]

        # Chercher le nom du rôle dans la configuration
        for custom_name, data in CUSTOM_ROLES.items():
            if data["id"] == role.id:
                role_name = custom_name
                break

        # Si le rôle n'est pas dans la configuration
        if not role_name:
            await ctx.send(f"❌ Le rôle **{role.name}** n'est pas configuré comme rôle personnalisé.")
            return
    else:
        # Chercher d'abord dans la configuration
        role_input_lower = role_input.lower()
        if role_input_lower in CUSTOM_ROLES:
            role_name = role_input_lower
            role_id = CUSTOM_ROLES[role_name]["id"]
            role = discord.utils.get(ctx.guild.roles, id=role_id)
        else:
            # Chercher le rôle par nom
            role = discord.utils.get(ctx.guild.roles, name=role_input)

            # Si le rôle n'est pas trouvé, essayer de chercher de manière insensible à la casse
            if not role:
                for guild_role in ctx.guild.roles:
                    if guild_role.name.lower() == role_input.lower():
                        role = guild_role
                        break

            if role:
                # Chercher si ce rôle est déjà dans la configuration
                for custom_name, data in CUSTOM_ROLES.items():
                    if data["id"] == role.id:
                        role_name = custom_name
                        break

                # Si le rôle n'est pas dans la configuration
                if not role_name:
                    await ctx.send(f"❌ Le rôle **{role.name}** n'est pas configuré comme rôle personnalisé.")
                    return

    # Si le rôle n'est pas trouvé ou n'est pas dans la configuration
    if not role or not role_name:
        await ctx.send(f"❌ Le rôle **{role_input}** n'a pas été trouvé ou n'est pas configuré comme rôle personnalisé.")
        return

    # Vérifier si c'est un rôle protégé
    if role.id == MOD_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle modérateur (mod). Utilisez `!removeperm mod` pour modifier ses permissions.")
        return

    if role.id == HELPER_ROLE_ID:
        await ctx.send("⚠️ Ce rôle est configuré comme rôle helper. Utilisez `!removeperm helper` pour modifier ses permissions.")
        return

    # Retirer les commandes
    removed_commands = []
    for cmd in commands:
        # Supprimer le préfixe ! si présent
        if cmd.startswith("!"):
            cmd = cmd[1:]

        # Retirer la commande si elle existe
        if cmd in CUSTOM_ROLES[role_name]["permissions"]:
            CUSTOM_ROLES[role_name]["permissions"].remove(cmd)
            removed_commands.append(cmd)

    # Sauvegarder la configuration
    save_config()

    if removed_commands:
        commands_str = ", ".join([f"`!{cmd}`" for cmd in removed_commands])
        await ctx.send(f"✅ {len(removed_commands)} commande(s) retirée(s) du rôle **{role.name}** ({role_name}): {commands_str}")
    else:
        await ctx.send(f"ℹ️ Aucune commande retirée. Les commandes spécifiées n'étaient pas attribuées au rôle **{role.name}** ({role_name}).")

    # Afficher les commandes actuelles
    current_commands = ", ".join([f"`!{cmd}`" for cmd in CUSTOM_ROLES[role_name]["permissions"]]) if CUSTOM_ROLES[role_name]["permissions"] else "Aucune"
    await ctx.send(f"📋 Commandes actuelles pour **{role.name}** ({role_name}): {current_commands}")

# Commandes pour gérer les permissions des rôles
@bot.command(name="permissions", aliases=["perms", "showanyperms", "showperms", "listperms"])
async def show_permissions(ctx, role_input: str = None):
    """
    Affiche les permissions d'un rôle (standard ou personnalisé).

    Usage:
    !permissions [nom_du_role ou @mention]

    Exemples:
    !permissions mod
    !permissions helper
    !permissions support
    !permissions @Support
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Si aucun rôle n'est spécifié, afficher la liste des rôles disponibles
    if not role_input:
        embed = discord.Embed(
            title="🔑 Rôles disponibles",
            description="Voici la liste des rôles dont vous pouvez consulter les permissions :",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        # Rôles standards
        standard_roles = ["mod", "helper"]
        embed.add_field(
            name="Rôles standards",
            value="\n".join([f"- `{role}`" for role in standard_roles]),
            inline=False
        )

        # Rôles personnalisés
        if CUSTOM_ROLES:
            embed.add_field(
                name="Rôles personnalisés",
                value="\n".join([f"- `{role}`" for role in CUSTOM_ROLES.keys()]),
                inline=False
            )
        else:
            embed.add_field(
                name="Rôles personnalisés",
                value="Aucun rôle personnalisé configuré",
                inline=False
            )

        embed.add_field(
            name="💡 Astuce",
            value="Vous pouvez également mentionner directement un rôle pour voir ses permissions, par exemple: `!permissions @Support`",
            inline=False
        )

        embed.set_footer(text="Utilisez !permissions <nom_du_role> pour voir les permissions d'un rôle spécifique")
        await ctx.send(embed=embed)
        return

    # Trouver le rôle Discord et le nom dans la configuration
    role = None
    role_name = None
    is_standard_role = False

    # Vérifier d'abord si c'est une mention de rôle
    if ctx.message.role_mentions:
        role = ctx.message.role_mentions[0]

        # Vérifier si c'est un rôle standard par ID
        if role.id == MOD_ROLE_ID:
            role_name = "mod"
            is_standard_role = True
        elif role.id == HELPER_ROLE_ID:
            role_name = "helper"
            is_standard_role = True
        else:
            # Chercher le nom du rôle dans la configuration
            for custom_name, data in CUSTOM_ROLES.items():
                if data["id"] == role.id:
                    role_name = custom_name
                    break

            # Si le rôle n'est pas dans la configuration
            if not role_name:
                await ctx.send(f"❌ Le rôle **{role.name}** n'est pas configuré avec des permissions spécifiques.")
                return
    else:
        # Vérifier si c'est un rôle standard (mod ou helper)
        role_input_lower = role_input.lower()
        if role_input_lower in ["mod", "helper"]:
            role_name = role_input_lower
            is_standard_role = True
            role_id = MOD_ROLE_ID if role_name == "mod" else HELPER_ROLE_ID
            role = discord.utils.get(ctx.guild.roles, id=role_id)
        else:
            # Chercher d'abord dans la configuration des rôles personnalisés
            if role_input_lower in CUSTOM_ROLES:
                role_name = role_input_lower
                role_id = CUSTOM_ROLES[role_name]["id"]
                role = discord.utils.get(ctx.guild.roles, id=role_id)
            else:
                # Chercher le rôle par nom
                role = discord.utils.get(ctx.guild.roles, name=role_input)

                # Si le rôle n'est pas trouvé, essayer de chercher de manière insensible à la casse
                if not role:
                    for guild_role in ctx.guild.roles:
                        if guild_role.name.lower() == role_input.lower():
                            role = guild_role
                            break

                if role:
                    # Vérifier si c'est un rôle standard par ID
                    if role.id == MOD_ROLE_ID:
                        role_name = "mod"
                        is_standard_role = True
                    elif role.id == HELPER_ROLE_ID:
                        role_name = "helper"
                        is_standard_role = True
                    else:
                        # Chercher si ce rôle est déjà dans la configuration
                        for custom_name, data in CUSTOM_ROLES.items():
                            if data["id"] == role.id:
                                role_name = custom_name
                                break

                        # Si le rôle n'est pas dans la configuration
                        if not role_name:
                            await ctx.send(f"❌ Le rôle **{role.name}** n'est pas configuré avec des permissions spécifiques.")
                            return

    # Si le rôle n'est pas trouvé
    if not role:
        await ctx.send(f"❌ Le rôle **{role_input}** n'a pas été trouvé sur le serveur.")
        return

    # Créer l'embed de base
    embed = discord.Embed(
        title=f"🔒 Permissions du rôle {role.name}",
        color=role.color,
        timestamp=discord.utils.utcnow()
    )

    # Si c'est un rôle standard (mod ou helper)
    if is_standard_role:
        embed.description = f"Permissions pour {role.mention}\n{role_permissions[role_name]['description']}"

        # Diviser les commandes en groupes de 15 pour éviter de dépasser la limite de caractères
        commands = role_permissions[role_name]["commands"]
        chunks = [commands[i:i+15] for i in range(0, len(commands), 15)]

        for i, chunk in enumerate(chunks):
            embed.add_field(
                name=f"Commandes {i+1}" if i > 0 else "Commandes",
                value="```\n" + "\n".join([f"!{cmd}" for cmd in chunk]) + "```",
                inline=False
            )

        await ctx.send(embed=embed)
        return

    # Si c'est un rôle personnalisé
    if role_name in CUSTOM_ROLES:
        embed.description = f"Permissions pour le rôle personnalisé {role.mention}"

        # Diviser les commandes en groupes de 15 pour éviter de dépasser la limite de caractères
        commands = CUSTOM_ROLES[role_name]["permissions"]

        if not commands:
            embed.add_field(
                name="Commandes",
                value="```\nAucune commande configurée pour ce rôle```",
                inline=False
            )
        else:
            chunks = [commands[i:i+15] for i in range(0, len(commands), 15)]

            for i, chunk in enumerate(chunks):
                embed.add_field(
                    name=f"Commandes {i+1}" if i > 0 else "Commandes",
                    value="```\n" + "\n".join([f"!{cmd}" for cmd in chunk]) + "```",
                    inline=False
                )

        await ctx.send(embed=embed)
        return

    # Si on arrive ici, le rôle n'est pas configuré
    await ctx.send(f"❌ Le rôle **{role.name}** n'est pas configuré avec des permissions spécifiques.\n"
                  f"Rôles standards disponibles: `mod`, `helper`\n"
                  f"Rôles personnalisés disponibles: {', '.join([f'`{r}`' for r in CUSTOM_ROLES.keys()]) if CUSTOM_ROLES else 'Aucun'}")

@bot.command(name="staffperms", aliases=["staffperm"])
async def staff_permissions(ctx, role_type: str = None):
    """
    Affiche les permissions détaillées de tous les rôles de staff (owner, admin, mod, helper).

    Usage:
    !staffperms - Affiche un résumé de tous les rôles
    !staffperms owner - Affiche les détails du rôle propriétaire
    !staffperms admin - Affiche les détails du rôle administrateur
    !staffperms mod - Affiche les détails du rôle modérateur
    !staffperms helper - Affiche les détails du rôle helper
    """
    # Vérifier si l'utilisateur a la permission d'utiliser cette commande
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Vérifier si le type de rôle est valide
    valid_roles = ["owner", "admin", "mod", "helper"]
    if role_type and role_type.lower() not in valid_roles:
        await ctx.send(f"❌ Type de rôle invalide. Utilisez l'un des suivants : {', '.join(valid_roles)}")
        return

    # Créer l'embed de base
    embed = discord.Embed(
        title="👑 Hiérarchie et Permissions du Staff",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )

    # Obtenir les objets de rôle Discord
    owner_role = discord.utils.get(ctx.guild.roles, id=OWNER_ROLE_ID)
    admin_role = discord.utils.get(ctx.guild.roles, id=ADMIN_ROLE_ID)
    mod_role = discord.utils.get(ctx.guild.roles, id=MOD_ROLE_ID)
    helper_role = discord.utils.get(ctx.guild.roles, id=HELPER_ROLE_ID)

    # Définir les mentions de rôle ou texte par défaut
    owner_mention = owner_role.mention if owner_role else f"Rôle propriétaire (ID: {OWNER_ROLE_ID})"
    admin_mention = admin_role.mention if admin_role else f"Rôle administrateur (ID: {ADMIN_ROLE_ID})"
    mod_mention = mod_role.mention if mod_role else f"Rôle modérateur (ID: {MOD_ROLE_ID})"
    helper_mention = helper_role.mention if helper_role else f"Rôle helper (ID: {HELPER_ROLE_ID})"

    # Si un type de rôle spécifique est demandé
    if role_type:
        role_type = role_type.lower()

        if role_type == "owner":
            embed.description = f"## {owner_mention}\n\n**Niveau le plus élevé dans la hiérarchie**"
            embed.add_field(
                name="🔑 Permissions",
                value="- Accès complet à toutes les commandes du bot\n"
                      "- Seul à pouvoir agir sur d'autres propriétaires\n"
                      "- Peut configurer tous les aspects du serveur et du bot\n"
                      "- Peut modifier les permissions de tous les rôles\n"
                      "- Peut sanctionner n'importe quel membre, y compris les administrateurs",
                inline=False
            )
            embed.add_field(
                name="⚙️ Commandes exclusives",
                value="- Toutes les commandes d'administration\n"
                      "- Configuration des rôles (`!setownerrole`, `!setadminrole`, etc.)\n"
                      "- Gestion des permissions (`!addperm`, `!removeperm`, etc.)\n"
                      "- Configuration du serveur (`!setuptickets`, `!setupreglement`, etc.)",
                inline=False
            )
            embed.add_field(
                name="🛡️ Hiérarchie",
                value="- Peut agir sur : Propriétaires, Administrateurs, Modérateurs, Helpers, Membres\n"
                      "- Peut être ciblé par : Personne",
                inline=False
            )

        elif role_type == "admin":
            embed.description = f"## {admin_mention}\n\n**Second niveau dans la hiérarchie du staff**"
            embed.add_field(
                name="🔑 Permissions",
                value="- Accès complet à toutes les commandes du bot\n"
                      "- Peut configurer la plupart des aspects du serveur\n"
                      "- Peut modifier les permissions des modérateurs et helpers\n"
                      "- Peut sanctionner les modérateurs, helpers et membres",
                inline=False
            )
            embed.add_field(
                name="⚙️ Commandes exclusives",
                value="- Toutes les commandes de modération\n"
                      "- Configuration des rôles (`!setmodrole`, `!sethelperrole`)\n"
                      "- Gestion des permissions (`!addperm`, `!removeperm`)\n"
                      "- Configuration du serveur (`!setuptickets`, `!setupreglement`)",
                inline=False
            )
            embed.add_field(
                name="🛡️ Hiérarchie",
                value="- Peut agir sur : Administrateurs, Modérateurs, Helpers, Membres\n"
                      "- Peut être ciblé par : Propriétaires",
                inline=False
            )

        elif role_type == "mod":
            embed.description = f"## {mod_mention}\n\n**{role_permissions['mod']['description']}**"

            # Obtenir les commandes du modérateur
            mod_commands = role_permissions["mod"]["commands"]

            # Diviser les commandes en groupes pour éviter de dépasser la limite de caractères
            chunks = [mod_commands[i:i+15] for i in range(0, len(mod_commands), 15)]

            embed.add_field(
                name="🔑 Permissions",
                value="- Accès aux commandes de modération avancées\n"
                      "- Peut sanctionner les helpers et membres\n"
                      "- Peut gérer les tickets et les messages\n"
                      "- Peut attribuer et retirer certains rôles",
                inline=False
            )

            for i, chunk in enumerate(chunks):
                embed.add_field(
                    name=f"⚙️ Commandes {i+1}" if i > 0 else "⚙️ Commandes",
                    value="```\n" + "\n".join([f"!{cmd}" for cmd in chunk]) + "```",
                    inline=False
                )

            embed.add_field(
                name="🛡️ Hiérarchie",
                value="- Peut agir sur : Modérateurs, Helpers, Membres\n"
                      "- Peut être ciblé par : Propriétaires, Administrateurs",
                inline=False
            )

        elif role_type == "helper":
            embed.description = f"## {helper_mention}\n\n**{role_permissions['helper']['description']}**"

            # Obtenir les commandes du helper
            helper_commands = role_permissions["helper"]["commands"]

            # Diviser les commandes en groupes pour éviter de dépasser la limite de caractères
            chunks = [helper_commands[i:i+15] for i in range(0, len(helper_commands), 15)]

            embed.add_field(
                name="🔑 Permissions",
                value="- Accès aux commandes de modération de base\n"
                      "- Peut sanctionner les membres ordinaires\n"
                      "- Peut gérer les tickets et certains messages\n"
                      "- Permissions limitées par rapport aux modérateurs",
                inline=False
            )

            for i, chunk in enumerate(chunks):
                embed.add_field(
                    name=f"⚙️ Commandes {i+1}" if i > 0 else "⚙️ Commandes",
                    value="```\n" + "\n".join([f"!{cmd}" for cmd in chunk]) + "```",
                    inline=False
                )

            embed.add_field(
                name="🛡️ Hiérarchie",
                value="- Peut agir sur : Membres\n"
                      "- Peut être ciblé par : Propriétaires, Administrateurs, Modérateurs",
                inline=False
            )

    # Si aucun type de rôle n'est spécifié, afficher un résumé de tous les rôles
    else:
        embed.description = "Vue d'ensemble de la hiérarchie et des permissions du staff"

        # Propriétaire
        embed.add_field(
            name=f"👑 Propriétaire ({owner_mention})",
            value="- Niveau le plus élevé dans la hiérarchie\n"
                  "- Accès complet à toutes les commandes\n"
                  "- Peut agir sur tous les autres rôles\n"
                  "- Seul à pouvoir agir sur d'autres propriétaires",
            inline=False
        )

        # Administrateur
        embed.add_field(
            name=f"🔱 Administrateur ({admin_mention})",
            value="- Second niveau dans la hiérarchie\n"
                  "- Accès complet à toutes les commandes\n"
                  "- Peut agir sur les administrateurs, modérateurs, helpers et membres\n"
                  "- Ne peut pas agir sur les propriétaires",
            inline=False
        )

        # Modérateur - Afficher toutes les commandes sans résumé
        mod_commands_preview = ", ".join([f"`!{cmd}`" for cmd in role_permissions["mod"]["commands"]])

        embed.add_field(
            name=f"🔰 Modérateur ({mod_mention})",
            value=f"- {role_permissions['mod']['description']}\n"
                  f"- Peut agir sur les modérateurs, helpers et membres\n"
                  f"- Ne peut pas agir sur les propriétaires et administrateurs\n"
                  f"- Commandes: {mod_commands_preview}",
            inline=False
        )

        # Helper - Afficher toutes les commandes sans résumé
        helper_commands_preview = ", ".join([f"`!{cmd}`" for cmd in role_permissions["helper"]["commands"]])

        embed.add_field(
            name=f"🔹 Helper ({helper_mention})",
            value=f"- {role_permissions['helper']['description']}\n"
                  f"- Peut agir uniquement sur les membres\n"
                  f"- Ne peut pas agir sur les propriétaires, administrateurs et modérateurs\n"
                  f"- Commandes: {helper_commands_preview}",
            inline=False
        )

        embed.set_footer(text="Utilisez !staffperms <role> pour voir les détails d'un rôle spécifique")

    try:
        # Envoyer l'embed et stocker le message pour éviter les doublons
        sent_message = await ctx.send(embed=embed)
        print(f"Embed des staffperms envoyé avec succès (Message ID: {sent_message.id})")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'embed des staffperms: {e}")
        await ctx.send("Une erreur s'est produite lors de l'affichage des permissions du staff. Veuillez réessayer.")

@bot.command(name="addperm", aliases=["addanyperm"])
async def add_permission(ctx, role_input: str = None, command: str = None):
    """
    Ajoute une permission à un rôle (standard ou personnalisé).

    Usage:
    !addperm <nom_du_role ou @mention> <commande>

    Exemples:
    !addperm mod kick
    !addperm helper warn
    !addperm support mute
    !addperm @Support ban
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if not role_input or not command:
        await ctx.send("❌ Usage: `!addperm <nom_du_role ou @mention> <commande>`\n"
                      "Exemples:\n"
                      "`!addperm mod kick` - Ajoute la commande kick au rôle modérateur\n"
                      "`!addperm helper warn` - Ajoute la commande warn au rôle helper\n"
                      "`!addperm support mute` - Ajoute la commande mute au rôle personnalisé support\n"
                      "`!addperm @Support ban` - Ajoute la commande ban au rôle mentionné")
        return

    # Supprimer le préfixe ! si présent
    if command.startswith("!"):
        command = command[1:]

    # Trouver le rôle Discord et le nom dans la configuration
    role = None
    role_name = None
    is_standard_role = False

    # Vérifier d'abord si c'est un rôle standard (mod ou helper)
    role_input_lower = role_input.lower()
    if role_input_lower in ["mod", "helper"]:
        role_name = role_input_lower
        is_standard_role = True
        role_id = MOD_ROLE_ID if role_name == "mod" else HELPER_ROLE_ID
        role = discord.utils.get(ctx.guild.roles, id=role_id)
    else:
        # Vérifier si c'est une mention de rôle
        if ctx.message.role_mentions:
            role = ctx.message.role_mentions[0]

            # Vérifier si c'est un rôle standard par ID
            if role.id == MOD_ROLE_ID:
                role_name = "mod"
                is_standard_role = True
            elif role.id == HELPER_ROLE_ID:
                role_name = "helper"
                is_standard_role = True
            else:
                # Chercher le nom du rôle dans la configuration
                for custom_name, data in CUSTOM_ROLES.items():
                    if data["id"] == role.id:
                        role_name = custom_name
                        break

                # Si le rôle n'est pas dans la configuration, utiliser son nom comme identifiant
                if not role_name:
                    role_name = role.name.lower()
        else:
            # Chercher d'abord dans la configuration des rôles personnalisés
            if role_input_lower in CUSTOM_ROLES:
                role_name = role_input_lower
                role_id = CUSTOM_ROLES[role_name]["id"]
                role = discord.utils.get(ctx.guild.roles, id=role_id)
            else:
                # Chercher le rôle par nom
                role = discord.utils.get(ctx.guild.roles, name=role_input)

                # Si le rôle n'est pas trouvé, essayer de chercher de manière insensible à la casse
                if not role:
                    for guild_role in ctx.guild.roles:
                        if guild_role.name.lower() == role_input.lower():
                            role = guild_role
                            break

                if role:
                    # Vérifier si c'est un rôle standard par ID
                    if role.id == MOD_ROLE_ID:
                        role_name = "mod"
                        is_standard_role = True
                    elif role.id == HELPER_ROLE_ID:
                        role_name = "helper"
                        is_standard_role = True
                    else:
                        # Chercher si ce rôle est déjà dans la configuration
                        for custom_name, data in CUSTOM_ROLES.items():
                            if data["id"] == role.id:
                                role_name = custom_name
                                break

                        # Si le rôle n'est pas dans la configuration, utiliser son nom comme identifiant
                        if not role_name:
                            role_name = role.name.lower()

    # Si le rôle n'est pas trouvé
    if not role:
        await ctx.send(f"❌ Le rôle **{role_input}** n'a pas été trouvé sur le serveur.")
        return

    # Vérifier si c'est un rôle protégé (owner ou admin)
    if role.id == OWNER_ROLE_ID:
        await ctx.send("⚠️ Le rôle propriétaire (owner) a déjà toutes les permissions et ne peut pas être modifié.")
        return

    if role.id == ADMIN_ROLE_ID:
        await ctx.send("⚠️ Le rôle administrateur (admin) a déjà toutes les permissions et ne peut pas être modifié.")
        return

    # Vérifier si c'est un rôle par défaut (@everyone)
    if role.is_default():
        await ctx.send("⛔ Le rôle @everyone ne peut pas recevoir de permissions spécifiques.")
        return

    # Si c'est un rôle standard (mod ou helper)
    if is_standard_role:
        # Vérifier si la commande existe déjà dans les permissions du rôle
        if command in role_permissions[role_name]["commands"]:
            await ctx.send(f"⚠️ La commande `{command}` est déjà dans les permissions du rôle {role.name} ({role_name}).")
            return

        # Ajouter la commande aux permissions du rôle
        role_permissions[role_name]["commands"].append(command)
        save_permissions()
        await ctx.send(f"✅ La commande `{command}` a été ajoutée aux permissions du rôle {role.name} ({role_name}).")
        return

    # Si c'est un rôle personnalisé déjà dans la configuration
    if role_name in CUSTOM_ROLES:
        # Vérifier si la commande existe déjà dans les permissions du rôle
        if command in CUSTOM_ROLES[role_name]["permissions"]:
            await ctx.send(f"⚠️ La commande `{command}` est déjà dans les permissions du rôle {role.name} ({role_name}).")
            return

        # Ajouter la commande aux permissions du rôle
        CUSTOM_ROLES[role_name]["permissions"].append(command)
        save_config()
        await ctx.send(f"✅ La commande `{command}` a été ajoutée aux permissions du rôle {role.name} ({role_name}).")
        return

    # Si le rôle n'est pas encore dans la configuration, l'ajouter
    CUSTOM_ROLES[role_name] = {
        "id": role.id,
        "permissions": [command]
    }
    save_config()
    await ctx.send(f"✅ Le rôle **{role.name}** a été ajouté à la configuration sous le nom **{role_name}** avec la commande `{command}`.")

@bot.command(name="removeperm", aliases=["removeanyperm"])
async def remove_permission(ctx, role_input: str = None, command: str = None):
    """
    Retire une permission à un rôle (standard ou personnalisé).

    Usage:
    !removeperm <nom_du_role ou @mention> <commande>

    Exemples:
    !removeperm mod kick
    !removeperm helper warn
    !removeperm support mute
    !removeperm @Support ban
    """
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    if not role_input or not command:
        await ctx.send("❌ Usage: `!removeperm <nom_du_role ou @mention> <commande>`\n"
                      "Exemples:\n"
                      "`!removeperm mod kick` - Retire la commande kick du rôle modérateur\n"
                      "`!removeperm helper warn` - Retire la commande warn du rôle helper\n"
                      "`!removeperm support mute` - Retire la commande mute du rôle personnalisé support\n"
                      "`!removeperm @Support ban` - Retire la commande ban du rôle mentionné")
        return

    # Supprimer le préfixe ! si présent
    if command.startswith("!"):
        command = command[1:]

    # Trouver le rôle Discord et le nom dans la configuration
    role = None
    role_name = None
    is_standard_role = False

    # Vérifier d'abord si c'est un rôle standard (mod ou helper)
    role_input_lower = role_input.lower()
    if role_input_lower in ["mod", "helper"]:
        role_name = role_input_lower
        is_standard_role = True
        role_id = MOD_ROLE_ID if role_name == "mod" else HELPER_ROLE_ID
        role = discord.utils.get(ctx.guild.roles, id=role_id)
    else:
        # Vérifier si c'est une mention de rôle
        if ctx.message.role_mentions:
            role = ctx.message.role_mentions[0]

            # Vérifier si c'est un rôle standard par ID
            if role.id == MOD_ROLE_ID:
                role_name = "mod"
                is_standard_role = True
            elif role.id == HELPER_ROLE_ID:
                role_name = "helper"
                is_standard_role = True
            else:
                # Chercher le nom du rôle dans la configuration
                for custom_name, data in CUSTOM_ROLES.items():
                    if data["id"] == role.id:
                        role_name = custom_name
                        break

                # Si le rôle n'est pas dans la configuration
                if not role_name:
                    await ctx.send(f"❌ Le rôle **{role.name}** n'est pas configuré avec des permissions.")
                    return
        else:
            # Chercher d'abord dans la configuration des rôles personnalisés
            if role_input_lower in CUSTOM_ROLES:
                role_name = role_input_lower
                role_id = CUSTOM_ROLES[role_name]["id"]
                role = discord.utils.get(ctx.guild.roles, id=role_id)
            else:
                # Chercher le rôle par nom
                role = discord.utils.get(ctx.guild.roles, name=role_input)

                # Si le rôle n'est pas trouvé, essayer de chercher de manière insensible à la casse
                if not role:
                    for guild_role in ctx.guild.roles:
                        if guild_role.name.lower() == role_input.lower():
                            role = guild_role
                            break

                if role:
                    # Vérifier si c'est un rôle standard par ID
                    if role.id == MOD_ROLE_ID:
                        role_name = "mod"
                        is_standard_role = True
                    elif role.id == HELPER_ROLE_ID:
                        role_name = "helper"
                        is_standard_role = True
                    else:
                        # Chercher si ce rôle est déjà dans la configuration
                        for custom_name, data in CUSTOM_ROLES.items():
                            if data["id"] == role.id:
                                role_name = custom_name
                                break

                        # Si le rôle n'est pas dans la configuration
                        if not role_name:
                            await ctx.send(f"❌ Le rôle **{role.name}** n'est pas configuré avec des permissions.")
                            return

    # Si le rôle n'est pas trouvé ou n'est pas dans la configuration
    if not role or not role_name:
        await ctx.send(f"❌ Le rôle **{role_input}** n'a pas été trouvé ou n'est pas configuré avec des permissions.")
        return

    # Vérifier si c'est un rôle protégé (owner ou admin)
    if role.id == OWNER_ROLE_ID:
        await ctx.send("⚠️ Le rôle propriétaire (owner) a toutes les permissions par défaut et ne peut pas être modifié.")
        return

    if role.id == ADMIN_ROLE_ID:
        await ctx.send("⚠️ Le rôle administrateur (admin) a toutes les permissions par défaut et ne peut pas être modifié.")
        return

    # Si c'est un rôle standard (mod ou helper)
    if is_standard_role:
        # Vérifier si la commande existe dans les permissions du rôle
        if command not in role_permissions[role_name]["commands"]:
            await ctx.send(f"⚠️ La commande `{command}` n'est pas dans les permissions du rôle {role.name} ({role_name}).")
            return

        # Retirer la commande des permissions du rôle
        role_permissions[role_name]["commands"].remove(command)
        save_permissions()
        await ctx.send(f"✅ La commande `{command}` a été retirée des permissions du rôle {role.name} ({role_name}).")
        return

    # Si c'est un rôle personnalisé
    if role_name in CUSTOM_ROLES:
        # Vérifier si la commande existe dans les permissions du rôle
        if command not in CUSTOM_ROLES[role_name]["permissions"]:
            await ctx.send(f"⚠️ La commande `{command}` n'est pas dans les permissions du rôle {role.name} ({role_name}).")
            return

        # Retirer la commande des permissions du rôle
        CUSTOM_ROLES[role_name]["permissions"].remove(command)
        save_config()
        await ctx.send(f"✅ La commande `{command}` a été retirée des permissions du rôle {role.name} ({role_name}).")

        # Si le rôle n'a plus de permissions, demander si l'utilisateur veut le supprimer de la configuration
        if not CUSTOM_ROLES[role_name]["permissions"]:
            await ctx.send(f"ℹ️ Le rôle **{role.name}** ({role_name}) n'a plus aucune permission. Utilisez `!delrole {role_name}` si vous souhaitez le supprimer complètement.")
        return

@bot.command(name="resetperms")
async def reset_permissions(ctx, role_type: str = None):
    """Réinitialise les permissions d'un rôle (mod/helper) ou de tous les rôles."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    global role_permissions

    # Sauvegarder les permissions actuelles pour pouvoir les restaurer si nécessaire
    old_permissions = role_permissions.copy()

    if role_type and role_type.lower() not in ["mod", "helper", "all"]:
        await ctx.send("❌ Type de rôle invalide. Utilisez `mod`, `helper` ou `all`.")
        return

    # Définir les permissions par défaut
    default_permissions = {
        "mod": {
            "commands": [
                "kick", "mute", "unmute", "warn", "clearwarns", "clear",
                "addrole", "removerole", "addword", "removeword", "listwords",
                "renameticket", "addmember", "removemember", "listtickets"
            ],
            "description": "Modérateurs du serveur"
        },
        "helper": {
            "commands": [
                "warn", "mute", "unmute", "clear", "listwords",
                "renameticket", "addmember", "removemember", "listtickets"
            ],
            "description": "Assistants de modération"
        }
    }

    if not role_type or role_type.lower() == "all":
        # Réinitialiser toutes les permissions
        role_permissions = default_permissions.copy()
        save_permissions()
        await ctx.send("✅ Toutes les permissions des rôles ont été réinitialisées aux valeurs par défaut.")
    else:
        # Réinitialiser les permissions d'un rôle spécifique
        role_key = role_type.lower()
        role_permissions[role_key] = default_permissions[role_key].copy()
        save_permissions()
        await ctx.send(f"✅ Les permissions du rôle {role_key} ont été réinitialisées aux valeurs par défaut.")

# Lancement du bot
keep_alive()
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
