provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_container" "garfbot" {
  name  = "garfbot"
  image = "garfbot"
  
  restart = "always"
  
  volumes {
    container_path = "/usr/src/app"
    host_path      = "/home/crate/garfbot"
  }
}

resource "docker_container" "jonbot" {
  name  = "jonbot"
  image = "jonbot"
  
  restart = "always"
  
  volumes {
    container_path = "/usr/src/app"
    host_path      = "/home/crate/garfbot"
  }
}

resource "docker_container" "moneybot" {
  name  = "moneybot"
  image = "moneybot"
  
  restart = "always"
  
  volumes {
    container_path = "/usr/src/app"
    host_path      = "/home/crate/garfbot"
  }
}
