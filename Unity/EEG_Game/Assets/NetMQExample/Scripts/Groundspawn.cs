using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Groundspawn : MonoBehaviour
{   
    public GameObject[] obstaclePre;
    public float spawnTime = 1;
    private float timer = 0;
    void Start()
    {
        

    }

    // Update is called once per frame
    void Update()
    {
            if(timer > spawnTime)
            {
                int rand = Random.Range(0,obstaclePre.Length);
                GameObject obs  = Instantiate(obstaclePre[rand]);
                //Debug.Log(obs.transform.position);
                Debug.Log(transform.position);
                obs.transform.position = obs.transform.position;
                Destroy(obs,5);
                timer = 0;
            }
            timer  += Time.deltaTime;
    }
}
