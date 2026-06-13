package com.plataforma.academic;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;
import java.util.Map;
import java.util.HashMap;

@SpringBootApplication
@RestController
@RequestMapping("/api/academic")
public class AcademicApplication {

    public static void main(String[] args) {
        SpringApplication.run(AcademicApplication.class, args);
    }

    // Endpoint que recebe o ID do aluno
    @GetMapping("/alunos/{id}")
    public ResponseEntity<?> getAlunoInfo(@PathVariable int id) {
        RestTemplate restTemplate = new RestTemplate();
        
        // Define a URL do auth-service. Pega da variável de ambiente ou usa localhost por padrão
        String authServiceUrl = System.getenv().getOrDefault("AUTH_SERVICE_URL", "http://localhost:8081");
        
        try {
            // AQUI ACONTECE A INTEGRAÇÃO REST: O Java faz um GET no Python
            Map<String, Object> usuario = restTemplate.getForObject(authServiceUrl + "/api/users/" + id, Map.class);
            
            // Junta os dados do usuário com os dados acadêmicos
            Map<String, Object> resposta = new HashMap<>();
            resposta.put("usuario", usuario);
            resposta.put("curso", "Engenharia da Computação");
            resposta.put("semestre", 5);
            
            return ResponseEntity.ok(resposta);
            
        } catch (Exception e) {
            return ResponseEntity.status(404).body(Map.of("erro", "Aluno não encontrado no Auth Service"));
        }
    }
}