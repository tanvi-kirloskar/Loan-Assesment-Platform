data "aws_caller_identity" "current" {}

resource "aws_iam_role_policy" "ec2_parameters" {
  name = "loan-assessment-read-parameters"
  role = aws_iam_role.ec2.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]

        Resource = [
          aws_ssm_parameter.db_host.arn,
          aws_ssm_parameter.db_name.arn,
          aws_ssm_parameter.db_user.arn,
          aws_ssm_parameter.db_password.arn,
          aws_ssm_parameter.s3_bucket_name.arn,

          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/loan-assessment/GEMINI_API_KEY",
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/loan-assessment/JWT_SECRET_KEY"
        ]
      }
    ]
  })
}