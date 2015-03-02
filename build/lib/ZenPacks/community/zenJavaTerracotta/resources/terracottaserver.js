
(function(){
    var ZC = Ext.ns('Zenoss.component');

    function render_link(ob) {
        if (ob && ob.uid) {
            return Zenoss.render.link(ob.uid);
        } else {
            return ob;
        }
    }
    
    function pass_link(ob){ 
        return ob; 
    }
    
    ZC.TerracottaServerPanel = Ext.extend(ZC.ComponentGridPanel, {
        constructor: function(config) {
            config = Ext.applyIf(config||{}, {
                componentType: 'TerracottaServer',
                autoExpandColumn: 'name', 
                fields:                 [
                    {
                        "name": "uid"
                    }, 
                    {
                        "name": "severity"
                    }, 
                    {
                        "name": "status"
                    }, 
                    {
                        "name": "name"
                    }, 
                    {
                        "name": "getClientCount"
                    }, 
                    {
                        "name": "getIpserviceLink"
                    }, 
                    {
                        "name": "getJavaappLink"
                    }, 
                    {
                        "name": "getServerMode"
                    }, 
                    {
                        "name": "mbean"
                    }, 
                    {
                        "name": "server"
                    }, 
                    {
                        "name": "usesMonitorAttribute"
                    }, 
                    {
                        "name": "monitor"
                    }, 
                    {
                        "name": "monitored"
                    }, 
                    {
                        "name": "locking"
                    }
                ]
,
                columns:                [
                    {
                        "sortable": "true", 
                        "width": 50, 
                        "header": "Events", 
                        "renderer": Zenoss.render.severity, 
                        "id": "severity", 
                        "dataIndex": "severity"
                    }, 
                    {
                        "header": "Name", 
                        "width": 70, 
                        "sortable": "true", 
                        "id": "name", 
                        "dataIndex": "name"
                    }, 
                    {
                        "sortable": "true", 
                        "width": 120, 
                        "header": "Clients", 
                        "renderer": "pass_link", 
                        "id": "getClientCount", 
                        "dataIndex": "getClientCount"
                    }, 
                    {
                        "sortable": "true", 
                        "width": 120, 
                        "header": "IP Service", 
                        "renderer": "pass_link", 
                        "id": "getIpserviceLink", 
                        "dataIndex": "getIpserviceLink"
                    }, 
                    {
                        "sortable": "true", 
                        "width": 120, 
                        "header": "Java App", 
                        "renderer": "pass_link", 
                        "id": "getJavaappLink", 
                        "dataIndex": "getJavaappLink"
                    }, 
                    {
                        "sortable": "true", 
                        "width": 120, 
                        "header": "Mode", 
                        "renderer": "pass_link", 
                        "id": "getServerMode", 
                        "dataIndex": "getServerMode"
                    }, 
                    {
                        "sortable": "true", 
                        "width": 120, 
                        "header": "MBean", 
                        "renderer": "pass_link", 
                        "id": "mbean", 
                        "dataIndex": "mbean"
                    }, 
                    {
                        "sortable": "true", 
                        "width": 120, 
                        "header": "Server", 
                        "renderer": "pass_link", 
                        "id": "server", 
                        "dataIndex": "server"
                    }, 
                    {
                        "header": "Monitored", 
                        "width": 65, 
                        "sortable": "true", 
                        "id": "monitored", 
                        "dataIndex": "monitored"
                    }, 
                    {
                        "sortable": "true", 
                        "width": 65, 
                        "header": "Locking", 
                        "renderer": Zenoss.render.locking_icons, 
                        "id": "locking", 
                        "dataIndex": "locking"
                    }
                ]

            });
            ZC.TerracottaServerPanel.superclass.constructor.call(this, config);
        }
    });
    
    Ext.reg('TerracottaServerPanel', ZC.TerracottaServerPanel);
    ZC.registerName('TerracottaServer', _t('Terracotta Server'), _t('Terracotta Servers'));
    
    })();

