variable "aws_region" {
  type        = string
  description = "AWS region to deploy the infrastructure"
  default     = "us-east-1"
}

variable "aws_ec2_instance_type" {
  type        = string
  description = "AWS EC2 instance type tp use for ChromaDB deployment"
  default     = "m5.xlarge"
}

variable "aws_resource_tags" {
  description = "A map of tags to add to AWS resources"
  type = map(string)
  default = {
    Application = "set-streamlit-app-capstone-project"
  }
  
}

variable "key_name" {
  type = string
  description = "The name of your SSH key pair"
  default     =  "streamlit-app-key"

}