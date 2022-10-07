variable "ssh_pubkey" {
  type = string
  default = ""
}

resource "tls_private_key" "my_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "my_key_pair" {
  key_name   = var.key_name
  public_key = var.ssh_pubkey == "" ? tls_private_key.my_key.public_key_openssh : var.ssh_pubkey
}

output "private_key" {
  value     = tls_private_key.my_key.private_key_pem
  sensitive = true
}