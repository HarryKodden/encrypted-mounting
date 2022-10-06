// aws_security_group.tf

resource "aws_security_group" "my_security_group" {
  vpc_id = "${aws_vpc.my_vpc.id}"

  egress {
   from_port = 0
   to_port = 0
   protocol = "-1"
   cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    cidr_blocks = [
      "0.0.0.0/0"
    ]
    from_port = 22
      to_port = 22
      protocol = "tcp"
  }

  ingress {
    cidr_blocks = [
      "0.0.0.0/0"
    ]

    from_port = 80
      to_port = 80
      protocol = "tcp"
  }
  
  ingress {
    cidr_blocks = [
      "0.0.0.0/0"
    ]

    from_port = 443
      to_port = 443
      protocol = "tcp"
  }
}