// ansible.tf

resource "null_resource" "ansible" {
  triggers = {
    order = aws_eip.my_eip.id
  }

  provisioner "local-exec" {
    command = <<EOT
      if [ ! -f .env ]
      then
        export $(cat .env | xargs)
      fi
      ssh-keygen -R ${var.domain}
      echo -e "[workspace]\n${var.domain}" > /tmp/${var.domain}
      sleep 60
      ansible-playbook -u ${var.user_name} -i /tmp/${var.domain} playbook.yml
      rm /tmp/${var.domain}
    EOT
    interpreter = ["/bin/bash", "-c"]
    working_dir = "../ansible"
  }
}
