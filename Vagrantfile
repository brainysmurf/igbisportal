# -*- mode: ruby -*-
# vi: set ft=ruby :

# Install the 'hostsupdater' plugin for vagrant then run 'vagrant up' in this directory!
# $ vagrant plugin install vagrant-hostsupdater

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # The base box to use
  #config.vm.box = "chef/ubuntu-14.04"
  config.vm.box = "ubuntu/trusty64"

  # Provisioning script
  # adds stuff missing from the base box
  # turns out it has everything it needs though so this doesn't do much currently. but put stuff here if needed
  $script = <<SCRIPT
echo I am provisioning...
echo I am `whoami`   # you are root!

date > /etc/vagrant_provisioned_at

echo 'First update our repositories to the latest'
apt-get update
apt-get -y upgrade
echo 'Second install git'
apt-get -y install git
apt-get -y install curl   # pyenv may need this if wget isn't latest, anyway is useful
apt-get -y install libbz2-dev libxslt-dev   # this in particular is needed before installing python (which pyenv does from source)
apt-get -y install postgres-client libpq-dev postgresql-contrib postgresql  # needed for postgres

apt-get -y build-dep python-pip python-dev build-essential

echo 'Cloning git repositories'
cd /home/vagrant
su vagrant -c 'git clone https://github.com/yyuu/pyenv.git'
su vagrant -c 'git clone https://github.com/yyuu/pyenv-virtualenv.git pyenv/plugins/pyenv-virtualenv'

PROFILE=/home/vagrant/.bash_profile
echo 'export PYENV_VERSION=2.7.8' >> $PROFILE
echo 'Setting up our .bash_profile file'
echo 'export PYENV_ROOT="/home/vagrant/pyenv"' >> $PROFILE
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> $PROFILE
echo 'eval "$(pyenv init -)"' >> $PROFILE
echo 'eval "$(pyenv virtualenv-init -)"' >> $PROFILE
chown vagrant:vagrant $PROFILE

echo 'Installing virtualenv via pyenv'
su vagrant -c 'source '$PROFILE'; cd /home/vagrant/igbisportal; pyenv local 2.7.8; pyenv virtualenv igbisportal; pyenv local igbisportal'

echo 'Installing scrapy and scrapyd'
su vagrant -c 'cd /home/vagrant/igbisportal; pip install scrapy'

# from http://doc.scrapy.org/en/latest/topics/ubuntu.html
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 627220E7
echo 'deb http://archive.scrapy.org/ubuntu scrapy main' | tee /etc/apt/sources.list.d/scrapy.list
apt-get update && apt-get -y install scrapy-0.24

echo 'Finally, installing igbisportal'
cd /home/vagrant/igbisportal
su vagrant -c 'pip install -e .'

SCRIPT

  config.vm.network "private_network", ip: "192.168.70.10"
  config.vm.hostname = "igbisportal.vagrant"
  config.vm.network :forwarded_port, guest: 5432, host: 5000
  config.vm.network :forwarded_port, guest: 6543, host: 8888

  # Makes it accessible locally at igbisportal.vagrant (modifies the hosts file)
  config.hostsupdater.aliases = ["igbisportal.vagrant"]

  # Makes this directory available at /var/www/moodleclone/docroot on the virtual server
  config.vm.synced_folder "../igbisportal", "/home/vagrant/igbisportal", owner: "vagrant", group: "vagrant"

  # Provision script doesn't work to my liking, but still provided above as instructions on how to get things going
  #config.vm.provision "shell", inline: $script

  config.vm.provider :virtualbox do |vb|
      # This allows the virtual machine to use the host OS's VPN connection
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.gui = false

      # Following code that adjusts memory and CPU allocation is from 
      # http://www.stefanwrobel.com/how-to-make-vagrant-performance-not-suck

      host = RbConfig::CONFIG['host_os']
      # Give VM 1/4 system memory & access to all cpu cores on the host
      if host =~ /darwin/
        cpus = `sysctl -n hw.ncpu`.to_i
        # sysctl returns Bytes and we need to convert to MB
        mem = `sysctl -n hw.memsize`.to_i / 1024 / 1024 / 4
      elsif host =~ /linux/
        cpus = `nproc`.to_i
        # meminfo shows KB and we need to convert to MB
        mem = `grep 'MemTotal' /proc/meminfo | sed -e 's/MemTotal://' -e 's/ kB//'`.to_i / 1024 / 4
      else # sorry Windows folks, I can't help you
        cpus = 2
        mem = 1024
      end
   
      vb.customize ["modifyvm", :id, "--memory", mem]
      vb.customize ["modifyvm", :id, "--cpus", cpus]

  end


end
