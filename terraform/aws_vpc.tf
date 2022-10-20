// aws-vpc.tf

resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
}

resource "aws_eip" "my_eip" {
  instance = "${aws_instance.my_instance.id}"
  vpc = true
}