
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
    
    ZC.TerracottaClientPanel = Ext.extend(ZC.ComponentGridPanel, {
        constructor: function(config) {
            config = Ext.applyIf(config||{}, {
                componentType: 'TerracottaClient',
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
                        "name": "getCacheManagerState"
                    }, 
                    {
                        "name": "getClusterConnectionState"
                    }, 
                    {
                        "name": "getIpserviceLink"
                    }, 
                    {
                        "name": "getJavaappLink"
                    }, 
                    {
                        "name": "getTerracottaserverLink"
                    }, 
                    {
                        "name": "serverport"
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
                        "header": "Cache Manager Status", 
                        "renderer": "pass_link", 
                        "id": "getCacheManagerState", 
                        "dataIndex": "getCacheManagerState"
                    }, 
                    {
                        "sortable": "true", 
                        "width": 120, 
                        "header": "Cluster Connection Status", 
                        "renderer": "pass_link", 
                        "id": "getClusterConnectionState", 
                        "dataIndex": "getClusterConnectionState"
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
                        "header": "Terracotta Server", 
                        "renderer": "pass_link", 
                        "id": "getTerracottaserverLink", 
                        "dataIndex": "getTerracottaserverLink"
                    }, 
                    {
                        "sortable": "true", 
                        "width": 120, 
                        "header": "Server Port", 
                        "renderer": "pass_link", 
                        "id": "serverport", 
                        "dataIndex": "serverport"
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
            ZC.TerracottaClientPanel.superclass.constructor.call(this, config);
        }
    });
    
    Ext.reg('TerracottaClientPanel', ZC.TerracottaClientPanel);
    ZC.registerName('TerracottaClient', _t('Terracotta Client'), _t('Terracotta Clients'));
    
    })();

