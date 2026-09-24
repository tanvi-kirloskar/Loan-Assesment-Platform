# ---------------------------------------------------------
# Availability Zones
# ---------------------------------------------------------

data "aws_availability_zones" "available" {
  state = "available"
}


# ---------------------------------------------------------
# Public Subnet
# ---------------------------------------------------------

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.loan_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "loan-public-subnet"
  }
}


# ---------------------------------------------------------
# Private DB Subnet A
# ---------------------------------------------------------

resource "aws_subnet" "private_db_a" {
  vpc_id            = aws_vpc.loan_vpc.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name = "loan-private-db-subnet-a"
  }
}


# ---------------------------------------------------------
# Private DB Subnet B
# ---------------------------------------------------------

resource "aws_subnet" "private_db_b" {
  vpc_id            = aws_vpc.loan_vpc.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name = "loan-private-db-subnet-b"
  }
}


# ---------------------------------------------------------
# Internet Gateway
# ---------------------------------------------------------

resource "aws_internet_gateway" "loan_igw" {
  vpc_id = aws_vpc.loan_vpc.id

  tags = {
    Name = "loan-internet-gateway"
  }
}


# ---------------------------------------------------------
# Public Route Table
# ---------------------------------------------------------

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.loan_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.loan_igw.id
  }

  tags = {
    Name = "loan-public-route-table"
  }
}


# ---------------------------------------------------------
# Public Route Table Association
# ---------------------------------------------------------

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}


# ---------------------------------------------------------
# RDS DB Subnet Group
# ---------------------------------------------------------

resource "aws_db_subnet_group" "loan_db" {
  name = "loan-db-subnet-group"

  subnet_ids = [
    aws_subnet.private_db_a.id,
    aws_subnet.private_db_b.id
  ]

  tags = {
    Name = "loan-db-subnet-group"
  }
}