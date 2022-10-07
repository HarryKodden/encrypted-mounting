// ansible.tf

resource "null_resource" "store_key" {
  triggers = {
    order = aws_eip.my_eip.id
  }

  provisioner "local-exec" {
    command = <<EOT
      if [ ! -f .env ]
      then
        export $(cat .env | xargs)
      fi
      echo "${tls_private_key.my_key.private_key_pem}" > /tmp/${var.key_name}.pem
      chmod 600 /tmp/${var.key_name}.pem
    EOT
  }

}

resource "null_resource" "ansible" {
  triggers = {
    order = null_resource.store_key.id
  }

  provisioner "local-exec" {
    command = <<EOT
      if [ ! -f .env ]
      then
        export $(cat .env | xargs)
      fi
      ssh-keygen -R ${var.domain}
      echo "[workspace]\n${var.domain}" > /tmp/${var.domain}
      sleep 60
      ansible-playbook -u ${var.user_name} -i /tmp/${var.domain} playbook.yml --private-key /tmp/${var.key_name}.pem
      rm /tmp/${var.domain}
    EOT
    working_dir = "../ansible"
  }

}
