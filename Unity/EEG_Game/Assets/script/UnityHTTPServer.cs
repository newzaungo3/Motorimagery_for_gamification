using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net.Sockets;
using System.Net;
using System.IO;
using System.Threading;
using System.Diagnostics;
using System.Reflection;
using Debug = UnityEngine.Debug;


public class UnityHTTPServer : MonoBehaviour
{
    [SerializeField]
    public int port;
    [SerializeField]
    public string SaveFolder;
    [SerializeField]
    public bool UseStreamingAssetsPath = false;
    [SerializeField]
    public int bufferSize = 16;
    public static UnityHTTPServer Instance;

    public MonoBehaviour HttpController;

    SimpleHTTPServer myServer;
    void Awake()
    {
        Instance = this;
        DontDestroyOnLoad(gameObject);
        if (myServer == null)
        {
            Init();
        }
    }
    void Init()
    {
        StartServer();
    }

    public void StartServer()
    {
        // Create the Http server instance.
        // Server will automatically start once it created.
        // replace {} part with your parameters
        myServer = new SimpleHTTPServer(GetSaveFolderPath, port, HttpController, bufferSize);
        Debug.Log("Create Server");
        // Regist the OnJsonSerialized delegate to your json implemention.
        // Here, we use the Unity's JsonUtility.
        myServer.OnJsonSerialized += (result) =>
        {
            return JsonUtility.ToJson(result);
        };
        // Stop the server, remember to call the Stop() method while the application is close.
        //myServer.Stop();
    }
    string GetSaveFolderPath
    {
        get
        {
            if (UseStreamingAssetsPath)
            {
                return Application.streamingAssetsPath;
            }
            return SaveFolder;
        }
    }

    public void StopServer()
    {
        Application.Quit();
    }

    void OnApplicationQuit()
    {
        myServer.Stop();
    }

}