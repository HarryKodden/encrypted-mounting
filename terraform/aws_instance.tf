// aws_instance.tf

resource "aws_instance" "my_instance" {
  ami = var.ami
  instance_type = var.instance_type
  key_name = var.key_name
  security_groups = ["${aws_security_group.my_security_group.id}"]
  tags = {
    Name = var.instance_name
  }
  subnet_id = "${aws_subnet.my_subnet.id}"
}