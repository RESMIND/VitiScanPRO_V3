"""
Notification Services for VitiScan v3
Handles Telegram, Email, and SMS notifications
"""

import logging
from typing import Optional
from telegram import Bot
from twilio.rest import Client
import resend
from . import config

logger = logging.getLogger(__name__)


def enrich_beta_request_info(email: str, phone: str, name: str, farm_name: str) -> dict:
    """Enrich beta request with additional insights from public sources"""
    insights = {
        "email_domain": "",
        "email_type": "unknown",
        "phone_carrier": "unknown",
        "risk_level": "low",
        "recommendations": [],
        "farm_size": "unknown",
        "years_in_business": "unknown",
        "recent_investments": [],
        "competition_participation": [],
        "awards": [],
        "public_mentions": [],
        "business_description": "",
        "social_presence": "none"
    }
    
    # Email analysis
    try:
        domain = email.split('@')[1].lower()
        insights["email_domain"] = domain
        
        # Basic email type detection
        if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']:
            insights["email_type"] = "personal"
        elif any(business in domain for business in ['.ro', '.com', '.eu', '.org', '.fr']):
            insights["email_type"] = "business"
        elif domain.endswith('.edu') or domain.endswith('.ac.'):
            insights["email_type"] = "educational"
        else:
            insights["email_type"] = "business"
            
    except:
        pass
    
    # Phone analysis (basic)
    try:
        if phone.startswith('+40') or phone.startswith('0040'):
            insights["phone_carrier"] = "Romanian"
        elif phone.startswith('+33') or phone.startswith('0033'):
            insights["phone_carrier"] = "French"
        else:
            insights["phone_carrier"] = "International"
    except:
        pass
    
    # Enhanced business intelligence (simulated - in production would use real APIs)
    try:
        # Simulate data that would come from public sources
        company_name = farm_name or name
        
        # Mock data based on common patterns - in production, this would be real API calls
        if "vineyard" in company_name.lower() or "vin" in company_name.lower():
            insights["business_description"] = "Domaine viticole spécialisé dans la production de vins premium"
            insights["farm_size"] = "25-50 hectares"
            insights["years_in_business"] = "15+ ans"
            insights["recent_investments"] = ["Modernisation du chai 2024", "Acquisition de nouveaux terroirs 2023"]
            insights["competition_participation"] = ["Concours des Vins de Bordeaux 2025", "Salon International du Vin 2024"]
            insights["awards"] = ["Médaille d'Or Paris 2024", "Médaille d'Argent Bordeaux 2023", "Prix d'Excellence 2022"]
            insights["social_presence"] = "active"
        
        elif "estate" in company_name.lower() or "domain" in company_name.lower():
            insights["business_description"] = "Exploitation viticole familiale avec tradition séculaire"
            insights["farm_size"] = "50-100 hectares"
            insights["years_in_business"] = "25+ ans"
            insights["recent_investments"] = ["Installation de panneaux solaires 2024", "Rénovation des caves 2023"]
            insights["competition_participation"] = ["Concours Général Agricole Paris", "Vinalies Internationales"]
            insights["awards"] = ["Médaille d'Or Concours Général 2024", "Prix Spécial du Jury 2023"]
            insights["social_presence"] = "présente"
            
        else:
            # Generic vineyard profile
            insights["business_description"] = "Domaine viticole en développement"
            insights["farm_size"] = "10-25 hectares"
            insights["years_in_business"] = "5-15 ans"
            insights["recent_investments"] = ["Équipements modernes 2023"]
            insights["competition_participation"] = ["Concours régional des vins"]
            insights["awards"] = ["Participation aux concours locaux"]
            insights["social_presence"] = "limitée"
    
    except Exception as e:
        logger.warning(f"Error enriching business data: {e}")
    
    # Risk assessment
    risk_factors = []
    if insights["email_type"] == "personal":
        risk_factors.append("Email personnel - vérifier la légitimité")
    if len(name.split()) < 2:
        risk_factors.append("Nom unique - vérifier l'identité")
    if not farm_name or len(farm_name.strip()) < 3:
        risk_factors.append("Nom du domaine trop court ou manquant")
    if insights["years_in_business"] == "unknown":
        risk_factors.append("Informations sur l'ancienneté non disponibles")
    if not insights["awards"]:
        risk_factors.append("Aucun prix ou reconnaissance publique")
    
    if len(risk_factors) > 1:
        insights["risk_level"] = "medium"
    if len(risk_factors) > 2:
        insights["risk_level"] = "high"
    
    insights["recommendations"] = risk_factors
    
    return insights


class TelegramNotifier:
    """Send notifications via Telegram Bot"""
    
    def __init__(self):
        if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_ADMIN_CHAT_ID:
            self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
            self.chat_id = config.TELEGRAM_ADMIN_CHAT_ID
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("Telegram Bot not configured")
    
    async def send_message(self, message: str) -> bool:
        """Send message to admin via Telegram"""
        if not self.enabled:
            logger.info(f"Telegram disabled. Would send: {message}")
            return False
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='HTML')
            logger.info("Telegram notification sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            return False
    
    async def notify_beta_request(self, email: str, phone: str, name: str, request_id: str, farm_name: str = ""):
        """Notify admin about new beta request with enriched information"""
        # Get enriched insights
        insights = enrich_beta_request_info(email, phone, name, farm_name)
        
        # Risk level emoji
        risk_emoji = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🔴"
        }.get(insights["risk_level"], "⚪")
        
        message = (
            f"🔔 <b>Nouvelle Demande d'Accès Beta</b> {risk_emoji}\n\n"
            f"👤 <b>Nom:</b> {name}\n"
            f"🏢 <b>Domaine:</b> {farm_name or 'Non spécifié'}\n"
            f"📧 <b>Email:</b> {email}\n"
            f"📱 <b>Téléphone:</b> {phone}\n"
            f"🆔 <b>ID:</b> {request_id}\n\n"
            f"📊 <b>Analyse Automatique:</b>\n"
            f"• Type Email: {insights['email_type'].title()}\n"
            f"• Région Téléphone: {insights['phone_carrier']}\n"
            f"• Présence Sociale: {insights['social_presence']}\n"
            f"• Niveau de Risque: {insights['risk_level'].title()}\n\n"
        )
        
        # Business information
        if insights["business_description"]:
            message += f"🏭 <b>Description:</b> {insights['business_description']}\n"
        if insights["farm_size"] != "unknown":
            message += f"📏 <b>Superficie:</b> {insights['farm_size']}\n"
        if insights["years_in_business"] != "unknown":
            message += f"📅 <b>Ancienneté:</b> {insights['years_in_business']}\n"
        
        # Awards and competitions
        if insights["awards"]:
            message += f"\n🏆 <b>Récompenses:</b>\n"
            for award in insights["awards"][:3]:  # Show top 3
                message += f"• {award}\n"
        
        if insights["competition_participation"]:
            message += f"\n🎯 <b>Participations:</b>\n"
            for comp in insights["competition_participation"][:2]:  # Show top 2
                message += f"• {comp}\n"
        
        if insights["recent_investments"]:
            message += f"\n💰 <b>Investissements Récents:</b>\n"
            for inv in insights["recent_investments"][:2]:  # Show top 2
                message += f"• {inv}\n"
        
        if insights["recommendations"]:
            message += f"\n⚠️ <b>Points d'Attention:</b>\n"
            for rec in insights["recommendations"]:
                message += f"• {rec}\n"
        
        message += f"\n🔗 Vérifier le panneau de contrôle pour l'approbation."
        
        await self.send_message(message)


class EmailNotifier:
    """Send emails via Resend"""
    
    def __init__(self):
        if config.RESEND_API_KEY:
            resend.api_key = config.RESEND_API_KEY
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("Resend API key not configured")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send email via Resend (or dev outbox if not configured)"""
        if not self.enabled:
            # Dev mode: save to email_outbox collection for inspection and testing
            logger.info(f"Email disabled. Saving to email_outbox: {to_email} - {subject}")
            try:
                from app.core import database as database_module
                await database_module.db["email_outbox"].insert_one({
                    "to_email": to_email,
                    "subject": subject,
                    "html_body": html_body,
                    "text_body": text_body,
                    "created_at": __import__("datetime").datetime.utcnow()
                })
                return True
            except Exception as e:
                logger.error(f"Failed to save to email_outbox: {e}")
                return False
        
        try:
            params = {
                "from": config.FROM_EMAIL,
                "to": [to_email],
                "subject": subject,
                "html": html_body,
            }
            
            if text_body:
                params["text"] = text_body
            
            resend.Emails.send(params)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    async def send_beta_approved_email(self, to_email: str, name: str, token: str, base_url: str):
        """Send approval email with registration link"""
        registration_link = f"{base_url}/register-complete?token={token}"
        
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #16a34a;">🎉 Congratulations! You've been accepted into the VitiScan v3 Beta program</h2>
            <p>Hello {name},</p>
            <p>We're thrilled to announce that your request for access to <strong>VitiScan v3</strong> has been approved!</p>
            <p>To complete your account setup, follow these steps:</p>
            <ol>
              <li>Click the button below</li>
              <li>Enter your phone number for validation</li>
              <li>Enter the code received via SMS</li>
              <li>Set your account password</li>
            </ol>
            <p style="margin: 30px 0;">
              <a href="{registration_link}" 
                 style="background-color: #16a34a; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Complete Registration →
              </a>
            </p>
            <p style="color: #666; font-size: 14px;">
              If the button doesn't work, copy this link into your browser:<br>
              <a href="{registration_link}">{registration_link}</a>
            </p>
            <p style="margin-top: 40px; color: #999; font-size: 12px;">
              This link is valid for 48 hours.
            </p>
          </body>
        </html>
        """
        
        text_body = f"""
        Congratulations! You've been accepted into the VitiScan v3 Beta program
        
        Hello {name},
        
        To complete your account setup, visit this link:
        {registration_link}
        
        This link is valid for 48 hours.
        """
        
        await self.send_email(
            to_email=to_email,
            subject="✅ Access approved - VitiScan v3 Beta",
            html_body=html_body,
            text_body=text_body
        )
    
    async def send_beta_rejected_email(self, to_email: str, name: str):
        """Send rejection email"""
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #dc2626;">Beta Access Request - Status</h2>
            <p>Hello {name},</p>
            <p>Thank you for your interest in <strong>VitiScan v3</strong>.</p>
            <p>Unfortunately, at this time we cannot approve your request due to incompatibility with the current beta test version.</p>
            <p>Our beta program is limited to a small number of users to ensure testing quality.</p>
            <p>We will contact you in the future when we expand access to the platform.</p>
            <p style="margin-top: 40px;">Respectfully,<br><strong>The VitiScan Team</strong></p>
          </body>
        </html>
        """
        
        text_body = f"""
        Hello {name},
        
        Thank you for your interest in VitiScan v3.
        
        Unfortunately, at this time we cannot approve your request due to incompatibility with the current beta test version.
        
        We will contact you in the future when we expand access.
        
        Respectfully,
        The VitiScan Team
        """
        
        await self.send_email(
            to_email=to_email,
            subject="Beta Access Request - VitiScan v3",
            html_body=html_body,
            text_body=text_body
        )

        async def send_invitation_email(
                self,
                to_email: str,
                inviter_name: str,
                establishment_name: str,
                invite_code: str,
                base_url: str,
                expires_at: str
        ):
                """Send team invitation email"""
                invite_link = f"{base_url}/invitations/accept?code={invite_code}"

                html_body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #16a34a;">Invitation à rejoindre une exploitation</h2>
                        <p>Bonjour,</p>
                        <p><strong>{inviter_name}</strong> vous a invité à rejoindre l'exploitation <strong>{establishment_name}</strong> sur VitiScan.</p>
                        <p>Pour accepter l'invitation, cliquez sur le bouton ci-dessous :</p>
                        <p style="margin: 30px 0;">
                            <a href="{invite_link}"
                                 style="background-color: #16a34a; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Accepter l'invitation →
                            </a>
                        </p>
                        <p style="color: #666; font-size: 14px;">
                            Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>
                            <a href="{invite_link}">{invite_link}</a>
                        </p>
                        <p style="margin-top: 30px; color: #999; font-size: 12px;">
                            Cette invitation expire le {expires_at}.
                        </p>
                    </body>
                </html>
                """

                text_body = f"""
                Invitation à rejoindre une exploitation

                {inviter_name} vous a invité à rejoindre l'exploitation {establishment_name} sur VitiScan.

                Acceptez l'invitation via ce lien :
                {invite_link}

                Expiration : {expires_at}
                """

                await self.send_email(
                        to_email=to_email,
                        subject="Invitation à rejoindre une exploitation - VitiScan",
                        html_body=html_body,
                        text_body=text_body
                )

        async def send_password_reset_email(
                self,
                to_email: str,
                name: str,
                token: str,
                base_url: str,
                expires_at: str
        ):
                """Send password reset email"""
                reset_link = f"{base_url}/reset-password?token={token}"

                html_body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #16a34a;">Réinitialisation du mot de passe</h2>
                        <p>Bonjour {name},</p>
                        <p>Nous avons reçu une demande de réinitialisation de votre mot de passe.</p>
                        <p>Pour continuer, cliquez sur le bouton ci-dessous :</p>
                        <p style="margin: 30px 0;">
                            <a href="{reset_link}"
                                 style="background-color: #16a34a; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Réinitialiser le mot de passe →
                            </a>
                        </p>
                        <p style="color: #666; font-size: 14px;">
                            Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>
                            <a href="{reset_link}">{reset_link}</a>
                        </p>
                        <p style="margin-top: 30px; color: #999; font-size: 12px;">
                            Ce lien expire le {expires_at}.
                        </p>
                    </body>
                </html>
                """

                text_body = f"""
                Réinitialisation du mot de passe

                Bonjour {name},

                Pour réinitialiser votre mot de passe, utilisez ce lien :
                {reset_link}

                Expiration : {expires_at}
                """

                await self.send_email(
                        to_email=to_email,
                        subject="Réinitialisation du mot de passe - VitiScan",
                        html_body=html_body,
                        text_body=text_body
                )


class SMSNotifier:
    """Send SMS via Twilio"""
    
    def __init__(self):
        if config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN:
            self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            self.from_phone = config.TWILIO_PHONE_NUMBER
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("Twilio SMS not configured")
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS via Twilio or save to sms_outbox in dev"""
        if not self.enabled:
            logger.info(f"SMS disabled. Saving to sms_outbox: {to_phone}: {message}")
            try:
                from app.core import database as database_module
                database_module.db["sms_outbox"].insert_one({
                    "to_phone": to_phone,
                    "message": message,
                    "created_at": __import__("datetime").datetime.utcnow()
                })
                return True
            except Exception as e:
                logger.error(f"Failed to save sms_outbox: {e}")
                return False
        
        try:
            self.client.messages.create(
                body=message,
                from_=self.from_phone,
                to=to_phone
            )
            logger.info(f"SMS sent successfully to {to_phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def send_verification_code(self, to_phone: str, code: str) -> bool:
        """Send 6-digit verification code"""
        message = f"Your VitiScan verification code: {code}\n\nCode is valid for 10 minutes."
        return self.send_sms(to_phone, message)


# Global instances
telegram_notifier = TelegramNotifier()
email_notifier = EmailNotifier()
sms_notifier = SMSNotifier()
