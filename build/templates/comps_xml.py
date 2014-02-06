template = '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE comps PUBLIC "-//Red Hat, Inc.//DTD Comps info//EN" "comps.dtd">
<comps>
        
  <group>
   <id>core</id>
   <default>false</default>
   <uservisible>true</uservisible>
   <display_order>1024</display_order>
   <name>core</name>
   <description>Contrail Distro </description>
    <packagelist>
{__packagesinfo__}
      <packagereq type="mandatory">contrail-install-packages</packagereq>
    </packagelist>
  </group>
</comps>
'''.strip('\n')