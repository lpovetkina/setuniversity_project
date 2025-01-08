
output "instance_public_ip" {
  value = module.streamlit_app_ec2_instance.public_ip
}

output "instance_public_dns" {
  value = module.streamlit_app_ec2_instance.public_dns
}

output "ec2_complete_public_ip" {
  description = "The public IP address assigned to the instance, if applicable. NOTE: If you are using an aws_eip with your instance, you should refer to the EIP's address directly and not use `public_ip` as this field will change after the EIP is attached"
  value       = module.streamlit_app_ec2_instance.public_ip
}
