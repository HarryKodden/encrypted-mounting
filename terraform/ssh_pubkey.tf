variable "default_ssh_pub" {
  type = string
  default = ""
}

data "local_file" "my_pubkey" {
  count = var.default_ssh_pub == "" ? 1 : 0
  filename = pathexpand("~/.ssh/id_rsa.pub")

}

resource "aws_key_pair" "my_admin" {
  key_name = var.key_name
  public_key = var.default_ssh_pub == "" ? data.local_file.my_pubkey[0].content : var.default_ssh_pub
}
