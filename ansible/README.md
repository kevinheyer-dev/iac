# Ansible SSH Access Setup for VMs

## Purpose

This guide outlines the necessary steps to configure SSH access for Ansible to manage your VMs. It covers SSH key setup, `sshd_config` adjustments, inventory configuration, and OpenBao integration for secure credential management.

---

## Prerequisites

- Ansible installed on your control node.
- OpenBao (or HashiCorp Vault) server configured and accessible.
- SSH access to the target VMs as a privileged user (e.g., `root` or `sudo` user).

---

## Step 1: Generate and Distribute SSH Keys

### 1.1 Generate SSH Key Pair

If you don't already have an SSH key pair for Ansible, generate one:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/ansible_key -C "ansible@control-node"
```

**Note:** Use a strong passphrase for the private key.

### 1.2 Distribute the Public Key

Copy the public key (`~/.ssh/ansible_key.pub`) to each VM:

```bash
ssh-copy-id -i ~/.ssh/ansible_key.pub user@vm-ip-address
```

Replace `user` and `vm-ip-address` with the appropriate values for each VM.

---

## Step 2: Configure `sshd_config` on VMs

### 2.1 Enable SSH Key Authentication

Ensure the following settings are present in `/etc/ssh/sshd_config` on each VM:

```ini
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

### 2.2 Restart SSH Service

After editing `sshd_config`, restart the SSH service:

```bash
sudo systemctl restart sshd
```

---

## Step 3: Configure Ansible Inventory

### 3.1 Inventory File Structure

Use a YAML-based inventory file (e.g., `inventory/production/hosts.yml`).  
Example:

```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 192.168.1.10
          ansible_user: ansible
    dbservers:
      hosts:
        db1.example.com:
          ansible_host: 192.168.1.20
          ansible_user: ansible
```

### 3.2 Store Host-Specific Variables in OpenBao

Store the `ansible_host` and `ansible_user` for each VM in OpenBao under the path `ansible/production/hosts/<hostname>`:

```bash
vault kv put ansible/production/hosts/web1.example.com \
  ansible_host="192.168.1.10" \
  ansible_user="ansible"
```