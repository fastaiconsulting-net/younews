# ---------------------------
# SES Configuration
# ---------------------------

# SES Domain Identity
resource "aws_ses_domain_identity" "main" {
  domain = var.ses_domain
}

# SES Domain DKIM
resource "aws_ses_domain_dkim" "main" {
  domain = aws_ses_domain_identity.main.domain
}

# SES Configuration Set for tracking
resource "aws_ses_configuration_set" "main" {
  name = "${local.project}-config-set"
}

# SES Template for Welcome Email
resource "aws_ses_template" "welcome" {
  name    = "${local.project}-welcome"
  subject = "Welcome to YouNews!"
  html    = <<EOF
<h1>Welcome to YouNews!</h1>

Thank you for subscribing to our newsletter. You'll receive:
<ul>
    <li>Daily AI-generated news summaries</li>
    <li>Market insights</li>
    <li>Tech updates</li>
</ul>

You can unsubscribe at any time using the unsubscribe link in our emails.

Best regards,
YouNews Team
EOF
}

# SES Email Identity (for sending from address)
resource "aws_ses_email_identity" "sender" {
  email = var.sender_email
}

# IAM policy for SES access
data "aws_iam_policy_document" "ses_access" {
  statement {
    sid    = "SESAccess"
    effect = "Allow"
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail",
      "ses:SendTemplatedEmail",
      "ses:GetTemplate",
      "ses:ListTemplates",
      "ses:DeleteTemplate",
      "ses:UpdateTemplate",
      "ses:CreateTemplate",
      "ses:VerifyEmailIdentity",
      "ses:DeleteIdentity",
      "ses:GetIdentityVerificationAttributes"
    ]
    resources = [
      "arn:aws:ses:${var.region}:${data.aws_caller_identity.current.account_id}:identity/*",
      "arn:aws:ses:${var.region}:${data.aws_caller_identity.current.account_id}:template/*",
      "arn:aws:ses:${var.region}:${data.aws_caller_identity.current.account_id}:configuration-set/*"
    ]
  }
}

resource "aws_iam_policy" "ses_policy" {
  name   = "${local.project}-ses"
  policy = data.aws_iam_policy_document.ses_access.json
}

resource "aws_iam_role_policy_attachment" "ses_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.ses_policy.arn
}
