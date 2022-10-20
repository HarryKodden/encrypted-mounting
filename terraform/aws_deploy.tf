// aws_deploy.tf

resource "local_file" "deploy_script" {
  filename        = "/tmp/deploy.sh"
  file_permission = "0755"
  content         = <<EOT
#!/bin/bash
# Generated file !
ssh-keygen -R ${var.domain}
echo -e "[workspace]\n${var.domain}" > /tmp/${var.domain}
export $(cat ${path.cwd}/../ansible/.env | xargs) && ansible-playbook -u ${var.user_name} -i /tmp/${var.domain} ${path.cwd}/../ansible/playbook.yml --private-key /tmp/${var.key_name}.pem
EOT
}
