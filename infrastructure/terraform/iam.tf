# ---------------------------------------------------------
# EC2 IAM Role
# ---------------------------------------------------------

resource "aws_iam_role" "ec2" {
  name = "loan-assessment-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ec2.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "loan-assessment-ec2-role"
  }
}


# ---------------------------------------------------------
# Session Manager Permissions
# ---------------------------------------------------------

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}


# ---------------------------------------------------------
# EC2 Instance Profile
# ---------------------------------------------------------

resource "aws_iam_instance_profile" "ec2" {
  name = "loan-assessment-ec2-profile"
  role = aws_iam_role.ec2.name
}