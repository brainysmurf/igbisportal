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
  config.vm.box = "hashicorp/precise64"

  # Provisioning script
  # adds stuff missing from the base box
  # turns out it has everything it needs though so this doesn't do much currently. but put stuff here if needed
  $script = <<SCRIPT
echo I am provisioning...
echo I am `whoami`

date > /etc/vagrant_provisioned_at

echo 'First update our repositories to the latest'
apt-get update
apt-get -y upgrade
echo 'Second install git'
apt-get -y install git
apt-get -y install curl   # pyenv may need this if wget isn't latest, anyway is useful

echo 'Cloning git repositories'
cd /home/vagrant
su vagrant -c 'git clone https://github.com/yyuu/pyenv.git'
su vagrant -c 'git clone https://github.com/yyuu/pyenv-virtualenv.git ~/pyenv/plugins/pyenv-virtualenv'

PROFILE=/home/vagrant/.bash_profile
echo 'Setting up our .bash_profile file'
echo 'export PYENV_ROOT="$HOME/pyenv"' >> $PROFILE
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> $PROFILE
echo 'eval "$(pyenv init -)"' >> $PROFILE
echo 'eval "$(pyenv virtualenv-init -)"' >> $PROFILE
chown vagrant:vagrant $PROFILE

echo 'Installing virtualenv via pyenv'
su vagrant -c 'source '$PROFILE'; cd ~; pyenv install 2.7'
su vagrant -c 'source '$PROFILE'; cd ~/openapply; pyenv version 2.7; pyenv virtualenv openapply; pyenv local openapply'

echo 'Installing scrapy and scrapyd'
su vagrant -c 'cd ~/openapply; pip install scrapy'

# from http://doc.scrapy.org/en/latest/topics/ubuntu.html
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 627220E7
echo 'deb http://archive.scrapy.org/ubuntu scrapy main' | tee /etc/apt/sources.list.d/scrapy.list
apt-get update && apt-get -y install scrapy-0.24

apt-get -y install scrapyd

SCRIPT

  config.vm.network "private_network", ip: "192.168.70.10"
  config.vm.hostname = "openapply.vagrant"

  # Makes it accessible locally at dragonnet.vagrant (modifies the hosts file)
  config.hostsupdater.aliases = ["openapply.vagrant"]

  # Makes this directory available at /var/www/moodleclone/docroot on the virtual server
  config.vm.synced_folder "../openapply", "/home/vagrant/openapply", owner: "vagrant", group: "vagrant"

  config.vm.provision "shell", inline: $script

  # This allows the virtual machine to use the host OS's VPN connection
  config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.gui = false

      # Following code that adjusts memory and CPU is from 
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
