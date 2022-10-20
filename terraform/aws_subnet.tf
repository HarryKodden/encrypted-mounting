// aws-subset.tf

resource "aws_subnet" "my_subnet" {
  cidr_block = "${cidrsubnet(aws_vpc.my_vpc.cidr_block, 3, 1)}"
  vpc_id = "${aws_vpc.my_vpc.id}"
  availability_zone = var.availability_zone
}

resource "aws_route_table" "my_routing_table" {
  vpc_id = "${aws_vpc.my_vpc.id}"
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.my_gateway.id}"
  }
}

resource "aws_route_table_association" "my_subnet_association" {
  subnet_id = "${aws_subnet.my_subnet.id}"
  route_table_id = "${aws_route_table.my_routing_table.id}"
}