using System;
using System.Collections;
using System.Threading;
using System.Collections.Generic;
using UnityEngine;
using AsyncIO;
using NetMQ;
using NetMQ.Sockets;

public class Server : MonoBehaviour
{
    Thread mThread;
    bool running;
    // Start is called before the first frame update
    void Start()
    {
        Debug.Log("Start");
        ThreadStart ts = new ThreadStart(Run);
        mThread = new Thread(ts);
        mThread.Start();
        running = true;
    }

    // Update is called once per frame

    void Update()
    {
        
    }

    void Run()
    {   
        AsyncIO.ForceDotNet.Force();
        Debug.Log("Create Server");
        using (var server = new ResponseSocket())
        {
            server.Bind("tcp://*:5555");
            while (true)
            {
                var message = server.ReceiveFrameString();
                Debug.Log("Received {0}" + message);
                // processing the request
                Thread.Sleep(100);
                Debug.Log("Sending World");
                server.SendFrame("World");
            }
        }
        NetMQConfig.Cleanup();
    }
}
