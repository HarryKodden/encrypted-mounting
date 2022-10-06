data "local_file" "my_pubkey" {
  filename = pathexpand("~/.ssh/id_rsa.pub")
}

resource "aws_key_pair" "my_admin" {
  key_name = var.key_name
  public_key = data.local_file.my_pubkey.content
}
