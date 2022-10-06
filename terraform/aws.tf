// aws.tf

variable "instance_name" {
  description = "Value of the Name tag for the EC2 instance"
  type        = string
  default     = "Encrypted Mounting Demo"
}

variable "region" {
  description = "AWS region to deploy"
  default = "us-east-1"
}

variable "availability_zone" {
  description = "AWS Availability Zone"
  default = "us-east-1a"
}

variable "ami" {
  description = "Ubuntu Server 20.04 LTS (HVM), SSD Volume Type"
  default = "ami-0149b2da6ceec4bb0"
}

variable "instance_type" {
  description = "AWS Instance Type"
  default = "t2.micro"
}

variable "user_name" {
  description = "administrator username"
  default = "ubuntu"
}

variable "key_name" {
  description = "SSH primary key to use"
  default = "administrator"
}

provider "aws" {
  region = var.region
}
